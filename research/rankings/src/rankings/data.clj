(ns rankings.data
  (:require [cheshire.core :as json]
            [clojure.java.io :as io]
            [clojure.set :refer [rename-keys]]
            [clojure.string :as str]))

(comment
  (cognitect.rebl/ui)
  nil)

(def data (-> "resources/mean_reciprocal_rank.3.json"
              io/reader
              (json/parse-stream)))

(defn keywordize-record
  [record]
  (rename-keys record {"freeze" :freeze
                       "user" :user
                       "queries" :queries}))

(defn split-by-query
  [record]
  (let [queries (->> record
                     :queries
                     vals
                     (mapcat keys)
                     (distinct))]
    (for [query queries]
      (assoc record :query query))))

(defn field-score
  [field]
  (if (str/includes? field "^")
    (let [[f score] (str/split field  #"\^")]
      [(keyword f) (Integer. score)])
    [(keyword field) 1]))

(defn field-str->field-map
  [s]
  (let [fields (str/split s #"\|")]
    (into {}
      (map field-score fields))))

(defn split-by-fields
  [{:keys [queries query] :as record}]
  (let [new-record (dissoc record :queries)]
    (for [[field-str scores] queries]
      (-> new-record
          (assoc :fields (field-str->field-map field-str))
          (assoc :score (get scores query))))))

(def tidy-data
  (->> data
       keywordize-record
       split-by-query
       (mapcat split-by-fields)))
