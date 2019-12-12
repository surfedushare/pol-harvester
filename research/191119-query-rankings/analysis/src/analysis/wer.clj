(ns analysis.wer
  (:require [oz.core :as oz]))

(def wer-data
  [{:ref "e37cc75ca339d8acafecaf206077b5b87ea3d9f0" :wer 0.35528942115768464}
   {:ref "3f1334d5ad738df124b8101ed9ca7bcd0a9bd6af" :wer 0.42463235294117646}
   {:ref "6f0a2e81ae1a44c6ae0c042240f5fd56431082d5" :wer 0.7872340425531915}
   {:ref "15ddb01499a5f225dd8202ed2cb70b4678f6c1a9" :wer 0.9743589743589743}
   {:ref "9b7f51cf9791be3e8164ab4d376eff69244f21a5" :wer 0.39572192513368987}
   {:ref "991e1d7b6bdb45c0f42dd276bf61b031125f10d3" :wer 0.2813278008298755}
   {:ref "8bc09299251cacf765f8f7fce0b4cf889e9b86ab" :wer 0.19464720194647203}
   {:ref "1855475608d211056950a21cafc2e8d02695f70d" :wer 0.40291583830351224}
   {:ref "403f11e235d9d6908df43918e20b05f586f39596" :wer 0.9869109947643979}
   {:ref "91906b3264195152197093179c9b2393570785c1" :wer 0.24863387978142076}
   {:ref "161722f39427833e03cca50e653bd21c6b1294de" :wer 0.29395604395604397}
   {:ref "b2adb47c2f3cba3d2f667ad9299c699b0ffce9ad" :wer 0.6911764705882353}
   {:ref "39651292687451ed6891e624be17c5894bc7008e" :wer 0.5050651230101303}
   {:ref "fd8af1a44e86d08b4a0fd9ce01297b0517f41d5b" :wer 0.4799566630552546}
   {:ref "5e472ac22c53c8b97b23762982f73f202a9d46f1" :wer 0.2744252873563218}
   {:ref "8e4633cc99d48d2582a1af34bc2fe56efcba8fbd" :wer 0.7718918918918919}
   {:ref "f1f29824ae6fc5d23e57ee1ab40a29ba3e2c4a43" :wer 0.46454767726161367}
   ;{:ref "00e93572eabca16047dcb58e4a992509ed89cfac" :wer 2.7777777777777777}
   {:ref "d2da6c29e0818165c1d7f050be65638ccbfc7e65" :wer 0.8980301274623407}
   {:ref "787c8de1664949d8e903e5ea1ee1fcdc66c1ad7a" :wer 0.5540950455005056}
   {:ref "4278934d137850c2bf141c047ea8553d859be13b" :wer 0.9839228295819936}
   ;{:ref "d1d29a42dc8eb82dc72313e3726c80802894f201" :wer 1.3225806451612903}
   ;{:ref "36aa0090a06b448fd3479691de17b9b68500c031" :wer 14.125}
   {:ref "9239dd597f9e214cfa5a01114505692259a7ef26" :wer 0.42857142857142855}
   {:ref "ddb955dcea2906dfe2c253c3b0176bfc6c90f953" :wer 0.9824304538799414}
   {:ref "9798d7e7b79bc15123935c30854a209478701b13" :wer 0.3125}
   {:ref "4bce9d78609beac427849bbc5a715d90de855bee" :wer 0.6054836252856055}])

(def plot
  {:data {:values (map #(update % :wer * 100) wer-data)}

   :width 1000
   :height 800

   :mark :bar
   :encoding {:x {:bin true
                  :field :wer
                  :type :quantitative
                  :axis {:title "Word error rate (%)"
                         :titleFontSize 20
                         :labelFontSize 16}}
              :y {:aggregate :count
                  :type :quantitative
                  :axis {:title "Aantal video's"
                         :titleFontSize 20
                         :labelFontSize 16}}}})

(oz/view! plot)
