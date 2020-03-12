(ns analysis.plots
  (:require [analysis.import :refer [get-data]]
            [clojure.java.io :as io]
            [clojure.string :as str]
            [clojure.math.combinatorics :as combo]
            [oz.core :as oz]
            [cheshire.core :as json]))

(def beta-files
  (let [file? #(.isFile %)
        json? #(str/ends-with? (.getName %) ".json")
        dcg? #(str/starts-with? (.getName %) "dcg")
        files (-> "resources/200312/beta-descriptions"
                  io/file
                  file-seq)]
    (->> files
         (filter file?)
         (filter json?)
         (filter dcg?))))

(defn combine-title-fields
  [m]
  (let [title (get m "Titel")
        title-a (get m "Titel (geanalyseerd)")
        v (max title title-a)]
    (-> m
        (assoc "Titel" v)
        (dissoc "Titel (geanalyseerd)"))))

(defn combine-text-fields
  [m]
  (let [text (get m "Tekst")
        text-a (get m "Tekst (geanalyseerd)")
        v (max text text-a)]
    (-> m
        (assoc "Tekst" v)
        (dissoc "Tekst (geanalyseerd)"))))

(def beta-data (->> beta-files
                    get-data
                    (map combine-title-fields)
                    (map combine-text-fields)))

(def fields #{"Titel" "Omschrijving" "Sleutelwoorden" "Tekst"})

(def combos
  (drop 1 (combo/subsets (into [] fields))))

(defn combo->title
  [combo]
  (str/capitalize (str/join ", " combo)))

(defn combo->pred
  [combo]
  (let [combo-set (into #{} combo)
        preds (for [field fields]
                (if (contains? combo-set field)
                  (fn [m] (pos? (get m field)))
                  (fn [m] (zero? (get m field)))))]
    (apply every-pred preds)))

(defn data
  []
  (for [combo combos]
    {:title (combo->title combo)
     :values (->> beta-data
                  (filter (combo->pred combo))
                  (map :score))}))

(def summary-plot
  {:data {:values (data)}

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
