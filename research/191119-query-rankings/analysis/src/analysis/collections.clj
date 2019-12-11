(ns analysis.collections
  (:require [oz.core :as oz]))

(def collections-data
  [{:collection "Wikiwijs Maken hbo" :filetype "html" :count 2996}
   {:collection "Wikiwijs Maken hbo" :filetype "pdf" :count 131}
   {:collection "Wikiwijs Maken hbo" :filetype "zip" :count 128}
   {:collection "Wikiwijs Maken hbo" :filetype "word" :count 121}
   {:collection "Wikiwijs Maken hbo" :filetype "powerpoint" :count 70}
   {:collection "Wikiwijs Maken wo" :filetype "html" :count 958}
   {:collection "Wikiwijs Maken wo" :filetype "pdf" :count 75}
   {:collection "Wikiwijs Maken wo" :filetype "zip" :count 71}
   {:collection "Wikiwijs Maken wo" :filetype "word" :count 46}
   {:collection "Wikiwijs Maken wo" :filetype "excel" :count 5}
   {:collection "Stimuleringsregeling" :filetype "video" :count 416}
   {:collection "Stimuleringsregeling" :filetype "unknown" :count 319}
   {:collection "Stimuleringsregeling" :filetype "html" :count 140}
   {:collection "Stimuleringsregeling" :filetype "word" :count 126}
   {:collection "Stimuleringsregeling" :filetype "pdf" :count 108}
   {:collection "Leraar24" :filetype "video" :count 649}
   {:collection "Leraar24" :filetype "html" :count 345}
   {:collection "WUR Library4Learning" :filetype "video" :count 430}])

(def collections-plot
  {:data {:values collections-data}
   :mark :bar

   :width 1000
   :height 800

   :encoding {:x {:field :collection
                  :type :ordinal
                  :axis {:title "Collectie"
                         :titleFontSize 20
                         :labelFontSize 16}}
              :y {:field :count
                  :aggregate :sum
                  :type :quantitative
                  :axis {:title "Aantal materialen"
                         :titleFontSize 20
                         :labelFontSize 16}}
              :color {:field :filetype
                      :type :nominal
                      :title "Bestandstype"
                      :legend {:titleFontSize 20
                               :labelFontSize 16}}}})

(oz/view! collections-plot)


