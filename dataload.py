import numpy as np
import scipy.misc as sm
import cv2


class Dataload(object):

    def __init__(self, batch_size, label_path,img_height=32, img_width=1050):
        self.batch_size = batch_size
        self.input_img_height = img_height
        self.input_img_width = img_width
        self.label_path = label_path

        f = open(self.label_path, 'r')
        data = f.read()
        self.data_dict = eval(data)
        self.img_path_list = list(self.data_dict.keys())

        self.current_index = 0
        self.epoch = 0

    def get_train_batch(self):
        """
        获取训练batch
        :return:
        """
        if self.current_index + self.batch_size +1 > len(self.img_path_list):
            self.current_index = len(self.img_path_list) - self.batch_size - 1
            self.epoch += 1

        batch_data = np.zeros([self.batch_size,
                               self.input_img_height,
                               self.input_img_width])
        batch_label = []

        for i in range(self.batch_size):
            img = cv2.imread(self.img_path_list[self.current_index])
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            #print(np.shape(img))

            img_resized = self._resize_img(img)
            batch_data[i] = img_resized
            batch_label.append(self.data_dict[self.img_path_list[self.current_index]])
            self.current_index += 1

        batch_label = self._sparse_tuple_from(batch_label)

        if self.current_index + 1 == len(self.img_path_list):
            self.current_index = 0

        batch_data = np.reshape(batch_data, [self.batch_size,
                                             self.input_img_width,
                                             self.input_img_height,
                                             1])

        batch_data = batch_data / 255 * 2 - 1

        return batch_data, batch_label

    def _resize_img(self, img):
        """
        将图像先转为灰度图，并将图像进行resize
        :param img:
        :return:
        """
        height, width = np.shape(img)

        if width > self.input_img_width:
            width = self.input_img_width
            ratio = float(self.input_img_width) / width
            outout_img = cv2.resize(img, (self.input_img_width,self.input_img_height))
        else:
            outout_img = np.zeros([self.input_img_height, self.input_img_width])
            ratio = self.input_img_height / height
            img_resized = cv2.resize(img, (int(width * ratio),self.input_img_height))
            outout_img[:, 0:np.shape(img_resized)[1]] = img_resized

        return outout_img

    def _sparse_tuple_from(self, sequences, dtype=np.int32):
        """
        将矩阵转为稀疏矩阵存储方式
        :param sequences:
        :param dtype:
        :return:
        """

        indices = []
        values = []
        for n, seq in enumerate(sequences):
            indices.extend(zip([n] * len(seq), [i for i in range(len(seq))]))
            values.extend(seq)

        indices = np.asarray(indices, dtype=np.int64)
        values = np.asarray(values, dtype=dtype)
        shape = np.asarray([len(sequences), np.asarray(indices).max(0)[1] + 1], dtype=np.int64)

        return indices, values, shape

    def decode_batch(self, batch_data, batch_label):
        f = open('./data/word_onehot.txt', 'r')
        data = f.read()
        words_onehot_dict = eval(data)
        words_list = list(words_onehot_dict.keys())
        words_onehot_list = [words_onehot_dict[words_list[i]] for i in range(len(words_list))]

        for i in range(np.shape(batch_data)[0]):
            img = batch_data[i]
            words = ''

            for onehot in batch_label[i]:
                if onehot == -1:
                    continue
                words += words_list[words_onehot_list.index(onehot)]
            print(words)
            img = np.reshape(img,[32, 1050])
            cv2.imwrite('d.jpg', img)
            cv2.imshow('d',img)
            cv2.waitKey()



if __name__ == "__main__":
    a = Dataload(64, './data/dataset_label.txt')
    for i in range(200):

        print('index', a.current_index)
        print('epoch', a.epoch)
        b, c = a.get_train_batch()
        a.decode_batch(b,c)
        # for i in range(np.shape(b)[0]):
        #     img = b[i]
        #     cv2.imshow('d',img)
        #     cv2.waitKey(20000)

    #print(c)