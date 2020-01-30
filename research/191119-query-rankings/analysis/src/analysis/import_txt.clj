(ns analysis.import-txt
  (:require [clojure.java.io :as io]))

(comment
  (cognitect.rebl/ui)
  nil)

(defn get-files
  [dir-name]
  (let [files (->> (str "resources/200122/" dir-name)
                   io/file
                   file-seq
                   (filter #(.isFile %)))]
    (for [file files]
      {:type (keyword dir-name) :text (slurp file) :teacher (subs (.getName file) 0 7)})))

(defn parse-dcgs
  [text]
  (->> (re-seq #"DCG: ([\d.]+)" text)
       (map second)
       (map #(Double/parseDouble %))))

(defn parse-queries
  [text]
  (->> (re-seq #"([\w ]+)\n(?=-{2,})" text)
       (map second)))

(defn parse-text
  [partition? text]
  (let [queries (parse-queries text)
        dcgs (if partition?
               (partition 2 (parse-dcgs text))
               (parse-dcgs text))
        combined (partition 2 (interleave queries dcgs))]
    (for [[query ct] combined]
      (if partition?
        {:query query :control (first ct) :treatment (second ct)}
        {:query query :treatment ct}))))

(defn parse-file
  [partition? {:keys [type text teacher]}]
  (for [m (parse-text partition? text)]
    (-> m
        (assoc :type type)
        (assoc :teacher teacher))))

(def data (concat (->> ["prf" "c5_synonyms"]
                       (mapcat get-files)
                       (mapcat (partial parse-file true)))
                  (->> ["google_search"]
                       (mapcat get-files)
                       (mapcat (partial parse-file false)))))
