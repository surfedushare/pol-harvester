(ns analysis.import
  (:require
    [clojure.java.io :as io]
    [cheshire.core :as json]
    [clojure.string :as str]
    [clojure.set :as set]))

(def files
  (let [file? #(.isFile %)
        json? #(str/ends-with? (.getName %) ".json")
        files (-> "resources/"
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

(import-file (first files))

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

(def user-query-mapping)

(defn incorrect-datum?
  "Filters out incorrect datums
  quite a lot of datums have 0 values for
  their score because the user is not
  the one who made the ranking."
  [datum])




(def data
  (->> files
       (map import-file)
       (mapcat tidy-data)))
