import tensorflow as tf
import tensorflow_hub as hub


class Embedder():
        
    def __init__(self, url='https://tfhub.dev/google/elmo/3'):
        self.embedder = hub.Module(url)
    
    def preprocess(self, text):
        return text

    def tokenize(self, text):
        tokens = text.replace('\n', ' ').replace('\t', ' ').replace('\xa0', ' ')
        tokens = ' '.join(tokens.split()).split(' ')
        return tokens

    def embed(self, tokens):
        embedding = self.embedder(tokens,
                             signature='default',
                             as_dict=True)['default']
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            sess.run(tf.tables_initializer())
            x = sess.run(embedding)
        return x


if __name__ == "__main__":
    pass
