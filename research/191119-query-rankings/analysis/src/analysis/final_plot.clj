(ns analysis.final-plot
  (:require [analysis.plot :refer [sub-data] :rename {sub-data regular-data}]
            [analysis.new-plots :refer [sub-data] :rename {sub-data video-data}]
            [oz.core :as oz]
            [cheshire.core :as json]))

(def data
  (let [d (concat (map #(assoc % :type "Alle leermaterialen") regular-data)
                  (map #(assoc % :type "Alleen video's") video-data))
        calc-mean (fn [xs] (/ (apply + xs) (count xs)))]
    (map #(assoc % :mean (calc-mean (:values %))) d)))

(def cleaned-data
  (let [grouped (vals (group-by :title data))
        new-pair (fn [[all-data {:keys [mean] :as video-only}]]
                   [(update all-data :mean - mean)
                    video-only])]
    (mapcat new-pair grouped)))


(def final-plot
  {:data {:values cleaned-data}

   :width 1000
   :height 800

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
                         :labelFontSize 16}}

              :color {:field :type
                      :type :nominal
                      :title "Leermaterialen"
                      :legend {:titleFontSize 20
                               :labelFontSize 16}}}})

(oz/view! final-plot)

(comment
  (defn copy-plot
    [plot]
    (json/generate-stream plot
      (clojure.java.io/writer "/Users/jelmer/Desktop/plot.json")))

  (copy-plot final-plot)
  nil)
