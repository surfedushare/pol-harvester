(ns analysis.import
  (:require
    [clojure.java.io :as io]
    [cheshire.core :as json]
    [clojure.string :as str]
    [clojure.set :as set]))

(def files
  (let [file? #(.isFile %)
        json? #(str/ends-with? (.getName %) ".json")
        files (-> "resources/191121"
                  io/file
                  file-seq)]
    (->> files
         (filter file?)
         (filter json?))))

(defn import-file
  [file]
  (let [filename (.getName file)
        metric (-> filename
                   (str/replace #".\d+.json" "")
                   (str/replace #"_" "-"))
        json(-> file
                slurp
                (json/decode))]
    (-> json
        (set/rename-keys {"freeze" :freeze
                          "user" :user
                          "queries" :queries})
        (assoc :filename filename
               :metric metric))))

(defn field-multiplier
  [field]
  (let [keywordize (fn [s] (-> s
                               (str/replace #"_" "-")
                               (#(str "field-" %))
                               keyword))]
    (if (str/includes? field "^")
      (let [[f multiplier] (str/split field  #"\^")]
        [(keywordize f) (Integer. multiplier)])
      [(keywordize field) 1])))

(def multipliers
  {:field-keywords 0
   :field-text 0
   :field-text-plain 0
   :field-title 0
   :field-title-plain 0})

(defn parse-fields
  [fields-str]
  (merge multipliers
    (into {}
      (let [fields (str/split fields-str #"\|")]
        (map field-multiplier fields)))))

(defn tidy-data
  [{:keys [queries] :as data}]
  (flatten
    (for [[fields scores] queries]
      (for [[query score] scores]
        (merge (parse-fields fields)
               (-> data
                   (dissoc :queries)
                   (assoc :query query)
                   (assoc :score score)))))))

(defn rename-fields
  [m]
  (set/rename-keys m
    {:field-title "Titel (geanalyseerd)"
     :field-title-plain "Titel"
     :field-text "Tekst (geanalyseerd)"
     :field-text-plain "Tekst"
     :field-keywords "Sleutelwoorden"}))

(def data
  (->> files
       (map import-file)
       (mapcat tidy-data)
       (map rename-fields)))

(first data)
