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

(tap> beta-data)

(->> beta-data
     (filter (fn [m]
               (and (zero? (get m "Titel"))
                    (zero? (get m "Sleutelwoorden"))
                    (zero? (get m "Tekst"))
                    (pos? (get m "Omschrijving"))))))


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

(defn copy-plot
  [plot]
  (let [clipboard (.getSystemClipboard (java.awt.Toolkit/getDefaultToolkit))]
    (.setContents
      clipboard
      (StringSelection. (json/generate-string plot)) nil)))

(def used-fields-table
  {:data [{:name "input"
           :values [{"Titel" 1
                     "Omschrijving" 1
                     :score 1}
                    {"Titel" 1
                     "Omschrijving" 0
                     :score 2}]

           :transform [{:type :identifier
                        :as :id}]}]

    :width 400
    :height 500

    :scales [{:name "position"
              :type :band
              :range :width
              :padding 0.05
              :round true
              :domain {:data "input"
                       :field :id
                       :sort {:field :score
                              :order :descending}}}]

    :marks [{:type :group
             :name "barchart"
             :encode {:enter {:height {:value 250}
                              :width {:signal :width}}}

             :scales [{:name "y"
                       :type :linear
                       :nice true
                       :range [250 0]
                       :zero true
                       :domain {:data "input"
                                :field :score}}]

             :axes [{:orient :bottom
                     :scale "position"}
                    {:orient :left
                     :scale "y"}]

             :marks [{:type :rect
                      :from {:data "input"}
                      :encode {:enter {:x {:scale "position"
                                           :field :id}
                                       :width {:scale "position"
                                               :band 1}
                                       :y {:scale "y"
                                           :field :score}
                                       :y2 {:scale "y"
                                            :value 0}}}
                      :update {:fill {:value "steelblue"}}}]}]})

(copy-plot used-fields-table)


(oz/view! used-fields-table)



