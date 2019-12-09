(ns analysis.plot
  (:require [oz.core :as oz]
            [analysis.import :refer [data]]
            [cheshire.core :as json]))

(first data)

(def plot
  (let [field-names ["Titel (geanalyseerd)"
                     "Titel"
                     "Tekst (geanalyseerd)"
                     "Tekst"
                     "Sleutelwoorden"]]

    {:$schema "https://vega.github.io/schema/vega/v5.json"
     :signals [{:name "cellSize" :value 30}
               {:name "valueWidth" :value 400}]

     :data [{:name "rawData"
             :values data}

            {:name "aggrData"
             :source "rawData"
             :transform [{:type :aggregate
                          :groupby field-names
                          :fields [:score :score]
                          :ops [:mean :stdev]
                          :as [:mean :stdev]}
                         {:type :identifier
                          :as :id}]}

            {:name "fieldNames"
             :values field-names}

            {:name "fieldData"
             :source "aggrData"
             :transform [{:type :fold
                          :fields field-names
                          :as [:field :value]}]}]

     :scales [{:name "combinations"
               :type "band"
               :domain {:data "aggrData"
                        :field :id
                        :sort {:field "mean"
                               :op :mean
                               :order :descending}}
               :range {:step {:signal "cellSize"}}}]

     :layout {:align {:row "all"
                      :column "each"}
              :padding {:row 0
                        :column 10}}

     :projections []

     :axes []

     :legends []

     :marks [{:type :group
              :name "fields"

              :scales [{:name "fields"
                        :type "band"
                        :domain field-names
                        :range {:step {:signal "cellSize"}}}

                       {:name "color"
                        :type "linear"
                        :domain {:data "fieldData"
                                 :field :value}
                        :range {:scheme "blues"}}]

              :marks [{:type :rect
                       :from {:data "fieldData"}
                       :encode {:update {:x {:scale "fields"
                                             :field :field}
                                         :y {:scale "combinations"
                                             :field :id}
                                         :width {:scale "fields"
                                                 :band 1
                                                 :offset -1}
                                         :height {:scale "combinations"
                                                  :band 1
                                                  :offset -1}
                                         :fill {:scale "color" :field :value}}}}

                      {:type :text
                       :name "columns"
                       :from {:data "fieldData"}
                       :encode {:update {:x {:scale "fields"
                                             :field :field
                                             :band 0.5}
                                         :y {:offset -2}
                                         :text {:field :field}
                                         :fontSize {:value 18}
                                         :fontWeight {:value :normal}
                                         :angle {:value -90}
                                         :align {:value :left}
                                         :baseline {:value :middle}}}}]}

             {:type :group
              :name "values"
              :encode {:enter {:width {:signal "valueWidth"}}}

              :scales [{:name "values"
                        :type :linear
                        :domain [-0.2 1]
                        :range [0 {:signal "valueWidth"}]}]

              :marks [{:type :symbol
                       :from {:data "aggrData"}
                       :encode {:enter {:fill {:value "black"}
                                        :size {:value 40}}
                                :update {:xc {:scale "values"
                                              :field :mean}
                                         :yc {:scale "combinations" :field :id :band 0.5}}}}

                      {:type :rect
                       :from {:data "aggrData"}
                       :encode {:enter {:fill {:value "black"}
                                        :height {:value 0.5}}
                                :update {:y {:scale "combinations" :field :id :band 0.5}
                                         :x {:scale "values" :signal "datum.mean - datum.stdev"}
                                         :x2 {:scale "values" :signal "datum.mean + datum.stdev"}}}}]

              :axes [{:scale "values"
                      :orient "bottom"
                      :offset {:signal "length(data('aggrData')) * cellSize + 5"}}]}]}))

(oz/view! plot :mode :vega)

(comment
  (copy-plot plot)
  nil)
