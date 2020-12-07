# Code contributed and debugged by Bangxi Xiao
import gensim
from preprocessing import *


class ProcessR(object):
    def __init__(self,
                 text,
                 vs=100,
                 ws=5,
                 mc=2,
                 wks=4):
        self.text = text
        print('...{} Documents Loaded...'.format(len(self.text)))
        self.docs = self.preprocess_docs()
        self.tagged_docs = [gensim.models.doc2vec.TaggedDocument(doc, [i]) for i, doc in enumerate(self.docs)]
        self.model = self.d2v(vs, ws, mc, wks)
        self.doc_vs = self.doc_v()
        print('...Language Processing and Language Model Training Finished...')

    def preprocess_docs(self):
        # Including steps: removing punctuations,
        #                  removing duplicated white spaces,
        #                  remove numbers,
        #                  remove stopwords,
        #                  stemming the text.
        return gensim.parsing.preprocessing.preprocess_documents(self.text)

    def d2v(self, vs, ws, mc, wks):
        # reference: https://arxiv.org/pdf/1405.4053v2.pdf <Distributed Representations of Sentences and Documents>
        print('...Training Doc2Vector Model via Gensim.models.Doc2Vec...')
        model = gensim.models.doc2vec.Doc2Vec(self.tagged_docs,
                                              vector_size=vs,
                                              window=ws,
                                              min_count=mc,
                                              workers=wks,
                                              compute_loss=True)
        return model

    def doc_v(self):
        return [self.model[x[1][0]].tolist() for x in self.tagged_docs]

    def process_text(self, s):
        return gensim.parsing.preprocessing.preprocess_string(s)

    def infer(self, dv):
        return self.model.infer_vector(dv)