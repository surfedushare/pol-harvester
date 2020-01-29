(ns analysis.new-plots
  (:require [oz.core :as oz]
            [analysis.import-txt :refer [data]]
            [cheshire.core :as json]))

(-> data first)

(->> data)

(def plot
  {:data {:values data}

   :mark "bar"

   :encoding {:x {:field}}})
