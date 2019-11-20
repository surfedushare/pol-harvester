(ns analysis.explore
  (:require
    [analysis.import :refer [data]]
    [oz.core :as oz]
    [clojure.string :as str]))

(comment
  (-> data first keys)
  nil)

(defn field-total
  [datum]
  (let [get-fields (juxt :field-title
                         :field-keywords
                         :field-title-plain
                         :field-text
                         :field-text-plain)]
    (apply + (get-fields datum))))

; === per teacher ===

(defn teacher-plot
  [metric]
  (let [data (->> data
                  (filter #(= (:metric %) metric))
                  (map #(assoc % :field-total (field-total %))))]

    {:data {:values data}

     :title (str metric " teacher scatter plot")

     :mark {:type :point
            :filled true
            :tooltip {:content :data}}

     :encoding {:x {:field :user
                    :type :ordinal}
                :y {:field :score
                    :type :quantitative}
                :color {:field :field-total
                        :type :quantitative}}

     :width 600
     :height 700}))
(oz/view! (teacher-plot "dcg"))
; === based on field total ===

(defn scatter-plot
  [metric]
  (let [data (->> data
                  (filter #(= (:metric %) metric))
                  (map #(assoc % :field-total (field-total %))))]

    {:data {:values data}

     :title (str metric " scatter plot")

     :mark {:type :point
            :filled true
            :tooltip {:content :data}}

     :encoding {:x {:field :field-total
                    :type :quantitative}
                :y {:field :score
                    :type :quantitative}}

     :width 600
     :height 700}))
(oz/view! (scatter-plot "dcg"))
; === query length ===
(defn add-query-length
  [datum]
  (assoc datum :query-length (count (:query datum))))

(defn query-length-plot
  [metric]
  (let [data (->> data
                  (filter #(= (:metric %) metric))
                  (map add-query-length))]

    {:data {:values data}

     :title (str metric " query length")

     :mark {:type :point
            :filled true
            :tooltip {:content :data}}

     :encoding {:x {:field :query-length
                    :type :quantitative}
                :y {:field :score
                    :type :quantitative}}

     :width 600
     :height 700}))
(oz/view! (query-length-plot "dcg"))

; === group by used fields ===

(defn add-used-fields
  [datum]
  (let [fields [:field-title
                :field-keywords
                :field-title-plain
                :field-text
                :field-text-plain]
        used-fields (for [field fields]
                      (let [multiplier (get datum field)]
                        (if (> multiplier 0)
                          (str/replace (name field) #"field-" ""))))]
    (assoc datum :used-fields (str/join " " (remove nil? used-fields)))))

(defn used-fields-plot
  [metric]
  (let [data (->> data
                  (filter #(= (:metric %) metric))
                  (map add-used-fields))]

    {:data {:values data}

     :title (str metric " used fields")

     :mark :circle
            ;:filled true
            ;:tooltip {:content :data}}

     :encoding {:x {:field :used-fields
                    :type :nominal}
                :y {:field :score
                    :type :quantitative
                    :bin {:maxbins 10}}
                :size {:aggregate :count
                       :type :quantitative}}


     :width 600
     :height 700}))
(oz/view! (used-fields-plot "dcg"))

; === histogram ===

(def dcg-histogram
  (let [data (filter #(= (:metric %) "dcg") data)]
    {:data {:values data}

     :title "dcg histogram"

     :mark :bar

     :encoding {:x {:field :score
                    :bin true
                    :type :quantitative}
                :y {:aggregate :count
                    :type :quantitative}}

     :width 600
     :height 700}))
(oz/view! dcg-histogram)

(defn field-contribution
  [field]
  (let [data (->> data
                  (filter #(= (:metric %) "dcg")))]

    {:data {:values data}

     :title "field contribution"

     :mark :circle

     :encoding {:x {:field (str "field-" (name field))
                    :type :quantitative
                    :scale {:domain [0 2]}}
                :y {:field :score
                    :type :quantitative
                    :bin {:maxbins 10}}
                :size {:aggregate :count
                       :type :quantitative
                       :legend nil}}}))
(oz/view! [:div {:style {:display :flex
                         :flex-flow "row wrap"}}
           [:vega-lite (field-contribution :title)]
           [:vega-lite (field-contribution :title-plain)]
           [:vega-lite (field-contribution :text)]
           [:vega-lite (field-contribution :text-plain)]
           [:vega-lite (field-contribution :keywords)]])


(first data)

