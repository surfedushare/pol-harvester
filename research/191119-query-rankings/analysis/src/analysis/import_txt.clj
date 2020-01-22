(ns analysis.import-txt
  (:require [clojure.java.io :as io]))

(defn get-files
  [dir-name]
  (let [contents (->> (str "resources/200122/" dir-name)
                      io/file
                      file-seq
                      (filter #(.isFile %))
                      (map slurp))]
    (for [c contents]
      {:type (keyword dir-name) :text c})))

(def prf-files (get-files "prf"))

(defn parse-dcgs
  [text]
  (->> (re-seq #"DCG: ([\d.]+)" text)
       (map second)
       (map #(Double/parseDouble %))
       (partition 2)))

(defn parse-queries
  [text]
  (->> (re-seq #"([\w ]+)\n(?=-{2,})" text)
       (map second)))

(defn parse-text
  [text]
  (let [queries (parse-queries text)
        dcgs (parse-dcgs text)
        combined (partition 2 (interleave queries dcgs))]
    (for [[query [control prf]] combined]
      {:query query :control control :prf prf})))

(defn parse-file
  [{:keys [type text]}]
  (for [m (parse-text text)]
    (assoc m :type type)))

(mapcat parse-file prf-files)
