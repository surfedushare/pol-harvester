(ns analysis.new-plots
  (:require [oz.core :as oz]
            [analysis.import-txt :refer [data]]
            [cheshire.core :as json]))

(def usable-data
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

(def plot
  {:data {:values usable-data}

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

(oz/view! plot)


(comment
  (defn copy-plot
    [plot]
    (json/generate-stream plot
      (clojure.java.io/writer "/Users/jelmer/Desktop/plot.json")))

  (copy-plot plot)
  nil)
