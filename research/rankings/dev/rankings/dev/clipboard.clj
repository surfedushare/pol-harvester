(ns rankings.dev.clipboard
  (:require [clojure.pprint :as pp])
  (:import [java.awt.datatransfer StringSelection])
  (:refer-clojure :exclude [spit slurp]))

(defn clipboard
  []
  (.getSystemClipboard (java.awt.Toolkit/getDefaultToolkit)))

(defn spit
  [data]
  (let [s (with-out-str (pp/pprint data))]
    (.setContents (clipboard) (StringSelection. s) nil)))

(defn spit-raw
  [s]
  (.setContents (clipboard) (StringSelection. s) nil))
