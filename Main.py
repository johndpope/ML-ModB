import sys
from tensorflow.examples.tutorials.mnist import input_data
import Net
import numpy as np
import netFunctions as nf
import utils as ut
import matplotlib.pyplot as plt

ETA_MIN = 0.0001
ETA_MAX = 0.9999

argomenti = sys.argv
if len(argomenti) > 2:
    path = argomenti[2]
else:
    path = ""
mnist = input_data.read_data_sets(path + "MNIST_data/", one_hot=True)
print("Inserisci la dimensione del training set")
DIM_TRAINING_SET = ut.getUserAmount(200, len(mnist.train.images))
print("Inserisci la dimensione del validation set")
DIM_VALIDATION_SET = ut.getUserAmount(100, len(mnist.validation.images))
print("Inserisci la dimensione del test set")
DIM_TEST_SET = ut.getUserAmount(100, len(mnist.test.images))
training_set = []
validation_set = []
test_set = []
for i in range(DIM_TRAINING_SET):
    elem = {'input': mnist.train.images[i], 'label': mnist.train.labels[i]}
    training_set.append(elem)
    if i < DIM_TRAINING_SET:
        elem = {'input': mnist.validation.images[i], 'label': mnist.validation.labels[i]}
        validation_set.append(elem)
    if i < DIM_TEST_SET:
        elem = {'input': mnist.test.images[i], 'label': mnist.test.labels[i]}
        test_set.append(elem)

print("Scegli cosa vuoi fare dalla seguente lista:")
while True:
    print("0) Chiudi il programma\n"
          "1) Effettua un training di una rete neurale in maniera manuale\n"
          "2) Confronto tra training con PCA e training con rete autoassociativa\n")
    choice = ut.getUserAmount(0, 2)
    if choice == 0:
        sys.exit()
    elif choice == 1:
        print("Quanti strati interni vuoi all'interno della tua rete?")
        n_layers = ut.getUserAmount(1, 10)
        dimensions = np.empty(n_layers + 2)
        dimensions[0] = len(training_set[0]['input'])
        dimensions[n_layers + 1] = 10
        functions = {}
        for l in range(1, n_layers + 1):
            print("Inserisci il numero di nodi al livello {}".format(l))
            dimensions[l] = ut.getUserAmount(1, 900)
            functions[l] = ut.getActivation(l)
        functions[n_layers + 1] = ut.getActivation(n_layers + 1)
        NN = Net.Net(dimensions, functions, ut.getErrorFunc())
        print("inserisci il valore di eta : ")
        eta = ut.getUserAmount(ETA_MIN, ETA_MAX, True)
        print("inserisci il numero massimo di epoche : ")
        max_epoche = ut.getUserAmount(10, 3000)
        print("inserisci il valore di alpha per la Generalization Loss : ")
        alpha = ut.getUserAmount(1, 100)
        print("Vuoi utilizzare il learning batch o online?\n"
              "1) Batch\n"
              "2) Online\n")
        if ut.getUserAmount(1, 2) == 2:
            error_train, error_valid = NN.train_net_online(training_set, validation_set, max_epoche, eta, alpha)
        else:
            error_train, error_valid = NN.train_net_batch(training_set, validation_set, max_epoche, eta, alpha)
        if len(argomenti) == 1:
            ut.plotGraphErrors(error_train, error_valid, "Addestramento della rete senza riduzione delle dimensioni")
        else:
            ut.plotGraphErrors(error_train, error_valid, "Addestramento della rete senza riduzione delle dimensioni",
                               argomenti[1])
        risp_giuste = ut.getRightNetResponse(NN, test_set)
        print("La rete con input l'output interno della rete autoassociativa ha risposto correttamente a ", risp_giuste,
              "in percentuale ", 100 * risp_giuste / len(test_set), "%")
        print("\n" * 3)
        continue
    elif choice == 2:
        # TEST PCA
        print("Inserisci la soglia del quantitativo di informazione da preservare dalla PCA")
        soglia_pca = ut.getUserAmount(50, 100, True) / 100
        new_dataset, matrix_w = Net.PCA(mnist.train.images[:DIM_TRAINING_SET], soglia_pca)
        plt.imshow(np.ndarray.reshape(mnist.train.images[0], (28, 28)), cmap=plt.cm.binary)
        if len(argomenti) > 1:
            plt.savefig(argomenti[1] + "Immagine originale.png")
        else:
            plt.show()
        plt.imshow(np.ndarray.reshape(np.dot(new_dataset[0], matrix_w.transpose()), (28, 28)), cmap=plt.cm.binary)
        if len(argomenti) > 1:
            plt.savefig(argomenti[1] + "Immagine ridotta con la PCA.png")
        else:
            plt.show()
        training_set_PCA = []
        validation_set_PCA = []
        test_set_PCA = []
        for i in range(DIM_TRAINING_SET):
            elem = {'input': new_dataset[i], 'label': mnist.train.labels[i]}
            training_set_PCA.append(elem)
            if i < DIM_VALIDATION_SET:
                elem = {'input': np.dot(validation_set[i]['input'], matrix_w), 'label': mnist.validation.labels[i]}
                validation_set_PCA.append(elem)
            if i < DIM_TEST_SET:
                elem = {'input': np.dot(test_set[i]['input'], matrix_w), 'label': mnist.test.labels[i]}
                test_set_PCA.append(elem)
        dimensions = np.empty(3)
        print("DEFINIZIONE DELLA RETE SU CUI EFFETUARE IL TEST")
        dimensions[0] = len(training_set_PCA[0]['input'])
        print("inserisci il numero di nodi nello strato nascosto")
        dimensions[1] = ut.getUserAmount(1, 900)
        dimensions[2] = 10
        functions = {1: ut.getActivation(1), 2: ut.getActivation(2)}
        print("inserisci il valore di eta : ")
        eta = ut.getUserAmount(ETA_MIN, ETA_MAX, True)
        print("inserisci il numero massimo di epoche : ")
        max_epoche = ut.getUserAmount(10, 3000)
        print("inserisci il valore di alpha per la Generalization Loss : ")
        alpha = ut.getUserAmount(1, 100)
        error_function = ut.getErrorFunc()
        print("La rete per il test della PCA e della rete autoassociativa sarà composta da ", len(dimensions),
              "\ncon relativi numero di nodi per ogni livello ",
              dimensions, "\ne relative funzioni di attivazione ", functions)
        NN_PCA = Net.Net(dimensions, functions, error_function)
        err_train_PCA, err_valid_PCA = NN_PCA.train_net_batch(training_set_PCA, validation_set_PCA, max_epoche, eta,
                                                              alpha)
        if len(argomenti) == 1:
            ut.plotGraphErrors(err_train_PCA, err_valid_PCA, "Addestramento rete con input l'out dell PCA")
        else:
            ut.plotGraphErrors(err_train_PCA, err_valid_PCA, "Addestramento rete con input l'out dell PCA", argomenti[1])
        print("Rete con input della PCA addestrata\n\n")
        print("Creazione della rete autoassociativa")
        # Test Rete Autoassociativa
        # addestramento rete autoassociativa
        # genero dataset per training rete autoassociativa
        # training set
        training_set_R = []
        for i in range(DIM_TRAINING_SET):
            elem = {'input': mnist.train.images[i], 'label': mnist.train.images[i]}
            training_set_R.append(elem)
        # validation set
        validation_set_R = []
        for i in range(DIM_VALIDATION_SET):
            elem = {'input': mnist.validation.images[i], 'label': mnist.validation.images[i]}
            validation_set_R.append(elem)
        # creazione rete associativa
        hidden_layers = ut.getNumbHiddenLayerRA()
        dimensions_RA = np.empty(hidden_layers + 2)
        # fisso il numero di nodi del livello di input e del livello di output
        dimensions_RA[0] = dimensions_RA[hidden_layers + 1] = len(mnist.train.images[0])
        # fisso il numero di nodi interni
        if hidden_layers == 1:
            dimensions_RA[1] = len(training_set_PCA[0]['input'])
        else:
            dimensions_RA[2] = len(training_set_PCA[0]['input'])
            print("inserisci il numero di nodi del primo strato nascosto")
            dimensions_RA[1] = ut.getUserAmount(int(dimensions_RA[2] + 1), int(dimensions_RA[0] - 1))
            print("inserisci il numero di nodi del terzo strato nascosto")
            dimensions_RA[3] = ut.getUserAmount(int(dimensions_RA[2] + 1), int(dimensions_RA[0] - 1))
        # fisso le funzioni di attivazione per ogni livello
        functions_RA = {}
        for l in range(1, len(dimensions_RA)):
            functions_RA[l] = ut.getActivation(l)
        # inserimento parametri di learning
        print("inserisci il valore di eta : ")
        eta_RA = ut.getUserAmount(ETA_MIN, ETA_MAX, True)
        print("inserisci il numero massimo di epoche : ")
        max_epoche_RA = ut.getUserAmount(10, 3000)
        print("inserisci il valore di alpha per la Generalization Loss : ")
        alpha_RA = ut.getUserAmount(1, 100)
        print("La rete autoassociativa sarà composta da ",len(dimensions_RA),
              "\ncon relativi numero di nodi per ogni livello ",
              dimensions_RA, "\ne relative funzioni di attivazione ", functions_RA)
        NN_R = Net.Net(dimensions_RA, functions_RA, nf.sum_square)
        print("Addestramento della rete autoassociativa iniziato")
        err_train_R, err_valid_R = NN_R.train_net_batch(training_set_R, validation_set_R, max_epoche_RA, eta_RA, alpha_RA)
        if len(argomenti) == 1:
            ut.plotGraphErrors(err_train_R, err_valid_R, "Addestramento rete autoassociativa")
        else:
            ut.plotGraphErrors(err_train_R, err_valid_R, "Addestramento rete autoassociativa", argomenti[1])
        print("Addestramento della rete autoassociativa completato")
        print("conversione dataset con la rete autoassociativa")
        #stampa numeri di prova
        plt.imshow(np.ndarray.reshape(NN_R.predict(training_set_R[0]['input']), (28, 28)), cmap=plt.cm.binary)
        if len(argomenti) > 1:
            plt.savefig(argomenti[1] + "Immagine ridotta con rete autoassociativa.png")
        else:
            plt.show()
        # creazione data set con dimensione ridotta
        training_set_RA = []
        validation_set_RA = []
        test_set_RA = []
        # Creo una rete NN_R2 uguale a NN_R che non ha lo strato di output
        livelli_R2 = int(len(dimensions_RA) / 2) + 1
        NN_R2 = Net.Net(dimensions_RA[:livelli_R2], functions_RA, nf.sum_square)
        for l in range(1, livelli_R2 + 1):
            NN_R2.W[l] = NN_R.W[l]
            NN_R2.B[l] = NN_R.B[l]
        for i in range(DIM_TRAINING_SET):
            out = NN_R2.predict(training_set[i]['input'])
            elem = {'input': out, 'label': mnist.train.labels[i]}
            training_set_RA.append(elem)
            if i < DIM_VALIDATION_SET:
                out = NN_R2.predict(validation_set[i]['input'])
                elem = {'input': out, 'label': mnist.validation.labels[i]}
                validation_set_RA.append(elem)
            if i < DIM_TEST_SET:
                out = NN_R2.predict(test_set[i]['input'])
                elem = {'input': out, 'label': mnist.test.labels[i]}
                test_set_RA.append(elem)
        # Addestramento di una rete con le dimensioni del dataset ridotte con una rete associativa
        print("Creazione  e addestramento della rete con input l'out interno della rete autoassociativa")
        NN_RA = Net.Net(dimensions, functions, error_function)
        err_train_RA, err_valid_RA = NN_RA.train_net_batch(training_set_RA, validation_set_RA, max_epoche, eta, alpha)
        if len(argomenti) == 1:
            ut.plotGraphErrors(err_train_RA, err_valid_RA, "Addestramento rete con out interno della rete autoassociativa")
        else:
            ut.plotGraphErrors(err_train_RA, err_valid_RA,
                               "Addestramento rete con out interno della rete autoassociativa", argomenti[1])
        print("Elaborazione delle due reti cui rispettivi test set e calcolo delle risposte giuste")
        # PCA
        pca_giuste = ut.getRightNetResponse(NN_PCA, test_set_PCA)
        print("La rete con input l'output della PCA ha risposto correttamente a ", pca_giuste,
              "in percentuale ", 100 * pca_giuste / len(test_set_PCA), "%")
        # RA
        ra_giuste = ut.getRightNetResponse(NN_RA, test_set_RA)
        print("La rete con input l'output interno della rete autoassociativa ha risposto correttamente a ", ra_giuste,
              "in percentuale ", 100 * ra_giuste / len(test_set_RA), "%")

        print("\n" * 3)
        continue
