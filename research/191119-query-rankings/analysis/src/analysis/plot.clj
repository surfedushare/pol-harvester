(ns analysis.plot
  (:require [oz.core :as oz]
            [analysis.import :refer [data]]
            [cheshire.core :as json]))
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
             :values (filter #(= (:metric %) "dcg") data)}

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

(defn has-kvs?
  [m subset]
  (let [create-predicate (fn [[k v]] (fn [x] (v (get x k))))
        pred (apply every-pred (map create-predicate subset))]
    (pred m)))

(has-kvs? (first data) {"Titel" zero?})

(def sub-data
  (let [dcg-data (filter #(= (:metric %) "dcg") data)
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

   :width 500
   :height 400

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
                  :sort "-y"}
              :y {:field :mean
                  :type :quantitative
                  :title "Gemiddelde nDCG"}}})

(oz/view! summary-plot)

(comment
  (defn copy-plot
    [plot]
    (json/generate-stream plot
      (clojure.java.io/writer "/Users/jelmer/Desktop/plot.json")))

  (copy-plot summary-plot)
  nil)
