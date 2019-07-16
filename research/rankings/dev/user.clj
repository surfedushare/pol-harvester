(ns user
  (:require [rankings.dev.clipboard :as clipboard]))

(defn pbcopy
  [data]
  (clipboard/spit data))

(def spy #(do (println "DEBUG:" %) %))
