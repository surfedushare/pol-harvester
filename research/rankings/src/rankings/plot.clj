(ns rankings.plot
  (:require [oz.core :as oz]
            [rankings.data :refer [tidy-data]]
            [cheshire.core :as json]
            [rankings.dev.clipboard :refer [spit-raw]]))

(defn copy-plot
  [plot]
  (spit-raw
    (json/generate-string plot {:pretty true})))

(defn flatten-record
  [{:keys [fields] :as m}]
  (-> (apply merge m fields)
      (dissoc :fields)))

(def plot
  (let [field-names (->> tidy-data
                         (map :fields)
                         (mapcat keys)
                         distinct)
        data (map flatten-record tidy-data)]

    {:$schema "https://vega.github.io/schema/vega/v5.json"
     :width 300
     :height 300

     :signals [{:name "cellSize" :value 20}]

     :data [{:name "rawData"
             :values data}

            {:name "aggrData"
             :source "rawData"
             :transform [{:type :aggregate
                          :groupby field-names
                          :fields [:dcg :dcg]
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

     :scales [{:name "fields"
               :type "band"
               :domain field-names
               :range {:step {:signal "cellSize"}}}

              {:name "combinations"
               :type "band"
               :domain {:data "aggrData"
                        :field :id}
               :range {:step {:signal "cellSize"}}}

              {:name "color"
               :type "linear"
               :domain {:data "fieldData"
                        :field :value}
               :range {:scheme "blues"}}]

     :projections []

     :axes []

     :legends []

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
                                :fill {:scale "color"
                                       :field :value}}}}]}))



(comment
  (copy-plot plot)
  nil)
