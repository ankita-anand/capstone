import tensorflow as tf
import tensorflow_hub as hub
import spacy
import tqdm

class Embedder():
        
    def __init__(self, url='https://tfhub.dev/google/elmo/3'):
        self.embedder = hub.Module(url)
        self.nlp = spacy.load('en_core_web_md')
        
    def preprocess(self, text):
        text = [doc.replace('\n', ' ').replace('\t', ' ').replace('\xa0', ' ') for doc in tqdm.tqdm( text)]
        text =  [' '.join(doc.split())for doc in tqdm.tqdm(text)]
        return text

    def doc_tokenize(self, text):
        return [self.nlp(doc).char_span(0, len(doc)).string.strip() for doc in tqdm.tqdm(text)]

    def sent_tokenize(self, text):
        tokens = [doc.replace('\n', ' ').replace('\t', ' ').replace('\xa0', ' ') for doc in text]
        tokens = [' '.join(doc.split()).split(' ') for doc in tokens]
        tokens = [doc.sents for doc in tokens]
        return tokens
    
    def doc_embed(self, doc_tokens):
        embedding = self.embedder(doc_tokens,
                             signature='default',
                             as_dict=True)['default']
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            sess.run(tf.tables_initializer())
            x = sess.run(embedding)
        return x


if __name__ == "__main__":
    pass
