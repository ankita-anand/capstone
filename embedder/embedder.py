import tensorflow as tf
import tensorflow_hub as hub


class Embedder():
    url = "https://tfhub.dev/google/elmo/2"

    def __init__(self):
        pass

    def preprocess(self, text):
        return text

    def tokenize(self, text):
        tokens = text.replace('\n', ' ').replace('\t', ' ').replace('\xa0', ' ')
        tokens = ' '.join(tokens.split()).split(' ')
        return tokens

    def embed(self, tokens):
        embedder = hub.Module(Embedder.url)
        embedding = embedder(tokens,
                             signature='default',
                             as_dict=True)['default']
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            sess.run(tf.tables_initializer())
            x = sess.run(embedding)
        return x


if __name__ == "__main__":
    pass
