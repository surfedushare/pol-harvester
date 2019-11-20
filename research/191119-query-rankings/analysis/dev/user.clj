(ns user
  (:require [puget.printer :as puget])
  (:import [java.awt.datatransfer StringSelection]))

(defn clipboard
  []
  (.getSystemClipboard (java.awt.Toolkit/getDefaultToolkit)))

(defn clip
  [data]
  (let [s (with-out-str (puget/pprint data))]
    (.setContents (clipboard) (StringSelection. s) nil)))

(add-tap puget/cprint)

(def debug-a (atom nil))
(add-tap #(reset! debug-a %))