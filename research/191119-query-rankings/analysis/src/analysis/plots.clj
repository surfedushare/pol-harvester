(ns analysis.plots
  (:require [analysis.import :refer [get-data]]
            [clojure.java.io :as io]
            [clojure.string :as str]
            [clojure.math.combinatorics :as combo]))

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

(defn has-kvs?
  [m subset]
  (let [create-predicate (fn [[k v]] (fn [x] (v (get x k))))
        pred (apply every-pred (map create-predicate subset))]
    (pred m)))

(def beta-data (->> beta-files
                    get-data
                    (map combine-title-fields)
                    (map combine-text-fields)))
