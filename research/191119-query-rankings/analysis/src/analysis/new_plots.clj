(ns analysis.new-plots
  (:require [oz.core :as oz]
            [analysis.import :refer [get-data]]
            [analysis.import-txt :refer [data]]
            [cheshire.core :as json]
            [clojure.java.io :as io]
            [clojure.string :as str]
            [clojure.set :as set]))

(def usable-experiment-data
  (let [copy-key (fn [m k nk]
                     (let [v (get m k)]
                       (assoc m nk v)))
        labels {:prf "PRF"
                :control "Controle"
                :google_search "Google"
                :c5_synonyms "ConceptNet"}
        update-label (fn [{:keys [type] :as m}]
                       (let [label (get labels type)]
                         (assoc m :type label)))
        control (->> data
                     (filter #(= (:type %) :prf))
                     (map #(assoc % :type :control))
                     (map #(copy-key % :control :value))
                     (map #(dissoc % :treatment :control)))
        new-data (->> data
                      (map #(copy-key % :treatment :value))
                      (map #(dissoc % :treatment :control)))]
    (->> (concat new-data control)
         (map update-label))))

(def experiment-plot
  {:data {:values (filter (comp #{"PRF" "Controle" "ConceptNet"} :type) usable-experiment-data)}

   :mark "bar"

   :width 600
   :height 700

   :encoding {:x {:field :type
                  :type :ordinal
                  :sort "-y"
                  :title "Experiment"
                  :axis {:titleFontSize 20
                         :labelFontSize 16}}
              :y {:aggregate :mean
                  :field :value
                  :type :quantitative
                  :title "Gemiddelde DCG"
                  :axis {:titleFontSize 20
                         :labelFontSize 16}}}})

(oz/view! experiment-plot)

; -- Kaldi benchmark

(def kaldi-data
  (-> (io/resource "200122/asr_benchmark/kaldi-time.json")
      slurp
      (json/parse-string true)))

(def clean-kaldi-data
  (let [parse (fn [[path transcribe-time video-time]]
                {:path path
                 :transcribe-time transcribe-time
                 :video-time video-time
                 :video-time-m (/ video-time 60)})
        calc-transcribe-rate (fn [{:keys [transcribe-time video-time]}]
                               (/ transcribe-time video-time))
        add-transcribe-rate (fn [m]
                              (assoc m :transcribe-rate (calc-transcribe-rate m)))]
     (->> kaldi-data
          (map parse)
          (map add-transcribe-rate))))

(def video-duration-histogram
  {:data {:values clean-kaldi-data}

   :mark :bar

   :width 700
   :height 450

   :encoding {:x {:bin true
                  :field :video-time-m
                  :type :quantitative
                  :title "Lengte video (minuten)"
                  :axis {:titleFontSize 20
                         :labelFontSize 16}}
              :y {:aggregate :count
                  :type :quantitative
                  :title "Aantal video's"
                  :axis {:titleFontSize 20
                         :labelFontSize 16}}}})

(oz/view! video-duration-histogram)

(def mean-transcribe-rate
  "The mean number of seconds it takes to transcribe
  a second of video (for 94 random English video's)
  Benchmarked on 1 cpu / 1 GB of memory"
  (let [data (map :transcribe-rate clean-kaldi-data)]
    (/ (apply + data) (count data))))
; ==> 1.0300807787846646 second/second video

; -- Just video rankings --

(def video-data-files
  (let [file? #(.isFile %)
        json? #(str/ends-with? (.getName %) ".json")
        files (-> "resources/200122/rankings_video_only"
                  io/file
                  file-seq)]
    (->> files
         (filter file?)
         (filter json?))))

(def video-data
  (get-data video-data-files))

(defn has-kvs?
  [m subset]
  (let [create-predicate (fn [[k v]] (fn [x] (v (get x k))))
        pred (apply every-pred (map create-predicate subset))]
    (pred m)))

(def sub-data
  (let [dcg-data (filter #(= (:metric %) "dcg") video-data)
        preds {"Alleen titel" #(or (has-kvs? % {"Titel (geanalyseerd)" pos?
                                                "Tekst (geanalyseerd)" zero?
                                                "Tekst" zero?
                                                "Sleutelwoorden" zero?})
                                   (has-kvs? % {"Titel" pos?
                                                "Tekst (geanalyseerd)" zero?
                                                "Tekst" zero?
                                                "Sleutelwoorden" zero?}))

               "Alleen tekst" #(or (has-kvs? % {"Titel" zero?
                                                "Titel (geanalyseerd)" zero?
                                                "Tekst (geanalyseerd)" pos?
                                                "Sleutelwoorden" zero?})
                                   (has-kvs? % {"Titel" zero?
                                                "Titel (geanalyseerd)" zero?
                                                "Tekst" pos?
                                                "Sleutelwoorden" zero?}))

               "Alleen sleutelwoorden" #(has-kvs? % {"Titel (geanalyseerd)" zero?
                                                     "Titel" zero?
                                                     "Tekst (geanalyseerd)" zero?
                                                     "Tekst" zero?
                                                     "Sleutelwoorden" pos?})

               "Titel en tekst" #(or (has-kvs? % {"Titel (geanalyseerd)" pos?
                                                  "Tekst (geanalyseerd)" pos?
                                                  "Sleutelwoorden" zero?})
                                     (has-kvs? % {"Titel" pos?
                                                  "Tekst" pos?
                                                  "Sleutelwoorden" zero?})
                                     (has-kvs? % {"Titel (geanalyseerd)" pos?
                                                  "Tekst" pos?
                                                  "Sleutelwoorden" zero?})
                                     (has-kvs? % {"Titel" pos?
                                                  "Tekst (geanalyseerd)" pos?
                                                  "Sleutelwoorden" zero?}))

               "Titel en sleutelwoorden" #(or (has-kvs? % {"Titel (geanalyseerd)" pos?
                                                           "Tekst (geanalyseerd)" zero?
                                                           "Tekst" zero?
                                                           "Sleutelwoorden" pos?})
                                              (has-kvs? % {"Titel" pos?
                                                           "Tekst (geanalyseerd)" zero?
                                                           "Tekst" zero?
                                                           "Sleutelwoorden" pos?}))

               "Tekst en sleutelwoorden" #(or (has-kvs? % {"Titel (geanalyseerd)" zero?
                                                           "Titel" zero?
                                                           "Tekst (geanalyseerd)" pos?
                                                           "Sleutelwoorden" pos?})
                                              (has-kvs? % {"Titel (geanalyseerd)" zero?
                                                           "Titel" zero?
                                                           "Tekst" pos?
                                                           "Sleutelwoorden" pos?}))

               "Titel, tekst en sleutelwoorden" #(or (has-kvs? % {"Titel (geanalyseerd)" pos?
                                                                  "Tekst (geanalyseerd)" pos?
                                                                  "Sleutelwoorden" pos?})
                                                     (has-kvs? % {"Titel" pos?
                                                                  "Tekst" pos?
                                                                  "Sleutelwoorden" pos?})
                                                     (has-kvs? % {"Titel (geanalyseerd)" pos?
                                                                  "Tekst" pos?
                                                                  "Sleutelwoorden" pos?})
                                                     (has-kvs? % {"Titel" pos?
                                                                  "Tekst (geanalyseerd)" pos?
                                                                  "Sleutelwoorden" pos?}))}]

    (for [[title pred] preds]
      {:title title :values (->> dcg-data
                                 (filter pred)
                                 (map :score))})))

(def summary-plot
  {:data {:values sub-data}

   :width 1000
   :height 800

   :transform [{:flatten [:values]
                :as [:score]}

               {:aggregate [{:op :mean
                             :field :score
                             :as :mean}]
                :groupby [:title]}]

   :mark :bar
   :encoding {:x {:field :title
                  :type :ordinal
                  :title "Gebruikte data"
                  :sort "-y"
                  :axis {:titleFontSize 20
                         :labelFontSize 16}}
              :y {:field :mean
                  :type :quantitative
                  :title "Gemiddelde nDCG"
                  :axis {:titleFontSize 20
                         :labelFontSize 16}}}})

(oz/view! summary-plot)

; -- Edurep comparison

(def edurep-files
  (let [file? #(.isFile %)
        json? #(str/ends-with? (.getName %) ".json")
        files (-> "resources/200122/edurep_comparison"
                  io/file
                  file-seq)]
    (->> files
         (filter file?)
         (filter json?))))

(def edurep-data
  (->> edurep-files
       (map (fn [f] [(.getName f)
                     (-> f
                         slurp
                         (json/parse-string true))]))))

(defn clean-edurep-data
  [[filename {:keys [results]}]]
  (let [type (case filename
               "edurep_with_filters.json" "EduRep (with filters)"
               "edurep_without_filters.json" "EduRep (without filters)")
        clean-teacher (fn [{:keys [docent] :as m}] (-> m
                                                       (assoc :teacher (str "docent" docent))
                                                       (dissoc :docent)))
        dissoc-stuff (fn [m] (dissoc m :result-count :dcg-array))
        add-type (fn [m] (assoc m :type type))
        rename-ks (fn [m] (set/rename-keys m {:query_string :query
                                              :dcg-score :value}))]
    (->> results
         (map clean-teacher)
         (map dissoc-stuff)
         (map add-type)
         (map rename-ks))))

(def usable-edurep-data
  (let [base (mapcat clean-edurep-data edurep-data)
        google-data (filter (comp #{"Google" "Controle"} :type) usable-experiment-data)]
    (concat base google-data)))

(def different-search-engines-plot
  {:data {:values usable-edurep-data}

   :mark "bar"

   :width 600
   :height 700

   :encoding {:x {:field :type
                  :type :ordinal
                  :sort "-y"
                  :title "Experiment"
                  :axis {:titleFontSize 20
                         :labelFontSize 16}}
              :y {:aggregate :mean
                  :field :value
                  :type :quantitative
                  :title "Gemiddelde DCG"
                  :axis {:titleFontSize 20
                         :labelFontSize 16}}}})

(oz/view! different-search-engines-plot)

; TODO: add edurep comparison

(comment
  (defn copy-plot
    [plot]
    (json/generate-stream plot
      (io/writer "/Users/jelmer/Desktop/plot.json")))

  (copy-plot different-search-engines-plot)
  nil)
