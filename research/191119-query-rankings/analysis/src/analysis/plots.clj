(ns analysis.plots
  (:require [analysis.import :refer [get-data]]
            [clojure.java.io :as io]
            [clojure.string :as str]
            [clojure.math.combinatorics :as combo]
            [oz.core :as oz]
            [cheshire.core :as json])
  (:import [java.awt.datatransfer StringSelection]))

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

(defn mean
  [& xs]
  (let [c (count xs)]
    (if (zero? c)
      0
      (/ (reduce + xs)
         c))))
(defn new-data
  []
  (for [combo combos]
    (let [base (merge (zipmap fields (repeat 0))
                      (zipmap combo (repeat 1)))
          scores (->> beta-data
                      (filter (combo->pred combo))
                      (map :score))]
      (assoc base :score (apply mean scores)))))

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

(defn copy-plot
  [plot]
  (let [clipboard (.getSystemClipboard (java.awt.Toolkit/getDefaultToolkit))]
    (.setContents
      clipboard
      (StringSelection. (json/generate-string plot)) nil)))

(def used-fields-table
  {:data [{:name "input"
           :values (new-data)
           :transform [{:type :identifier
                        :as :id}]}

          {:name "fields"
           :source "input"
           :transform [{:type :fold
                        :fields fields
                        :as [:field :used]}]}]

    :width 750
    :height 460

    :scales [{:name "position"
              :type :band
              :range :width
              :padding 0.05
              :round true
              :domain {:data "input"
                       :field :id
                       :sort {:field :score
                              :op :mean
                              :order :descending}}}]

    :marks [{:type :group
             :name "barchart"
             :encode {:enter {:height {:value 350}
                              :width {:signal :width}}}

             :scales [{:name "barcharty"
                       :type :linear
                       :nice true
                       :range [350 0]
                       :zero true
                       :domain {:data "input"
                                :field :score}}]

             :axes [{:orient :bottom
                     :scale "position"
                     :labels false
                     :ticks false}
                    {:orient :left
                     :scale "barcharty"
                     :labelFontSize 15
                     :title "Gemiddelde nDCG"
                     :titleFontSize 15}]

             :marks [{:type :rect
                      :from {:data "input"}
                      :encode {:enter {:x {:scale "position"
                                           :field :id}
                                       :width {:scale "position"
                                               :band 1}
                                       :y {:scale "barcharty"
                                           :field :score}
                                       :y2 {:scale "barcharty"
                                            :value 0}}}
                      :update {:fill {:value "steelblue"}}}]}

            {:type :group
             :name "boxes"
             :encode {:enter {:x {:value 0}
                              :y {:value 370}
                              :height {:value 80}
                              :width {:signal :width}}}

             :scales [{:name "fieldsy"
                       :type :band
                       :range [0 70]
                       :padding 0.05
                       :round true
                       :domain fields}
                      {:name "fieldscolor"
                       :type :ordinal
                       :domain [0 1]
                       :range ["transparent" "slategray"]}]

             :axes [{:orient :left
                     :scale "fieldsy"
                     :ticks false
                     :domainColor {:value "transparent"}
                     :labelFontSize 15
                     :title "Gebruikte velden"
                     :titleFontSize 15}]

             :marks [{:type :rect
                      :from {:data "fields"}
                      :encode {:enter {:x {:scale "position"
                                           :field :id}
                                       :width {:scale "position"
                                               :band 1}
                                       :y {:scale "fieldsy"
                                           :field :field}
                                       :height {:scale "fieldsy"
                                                :band 1}}
                               :update {:fill {:scale "fieldscolor"
                                               :field :used}}}}]}]})

(copy-plot used-fields-table)


(oz/view! used-fields-table)
