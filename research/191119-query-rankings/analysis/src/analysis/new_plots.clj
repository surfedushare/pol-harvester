(ns analysis.new-plots
  (:require [oz.core :as oz]
            [analysis.import-txt :refer [data]]
            [cheshire.core :as json]
            [clojure.java.io :as io]))

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
  {:data {:values usable-experiment-data}

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


(comment
  (defn copy-plot
    [plot]
    (json/generate-stream plot
      (io/writer "/Users/jelmer/Desktop/plot.json")))

  (copy-plot experiment-plot)
  nil)
