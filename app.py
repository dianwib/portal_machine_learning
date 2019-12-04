from flask import Flask, render_template, request
import cv2
from PIL import Image
import linearregressionmanual, logisticregressionmanual
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_diabetes
import numpy as np
import matplotlib.pyplot as plt


app = Flask(__name__)
@app.route('/')
@app.route('/index')
def hello_world():
	return render_template('index.html')

@app.route('/notes')
def hello_notes():
	return render_template('lecture_notes.html')

@app.route('/contact')
def hello_contact():
	return render_template('contact.html')


# @app.after_request
# def add_header(response):
#     '''
#     Add header to both force latest IE rendering engine or Chrome Frame,
#     and also to cache the rendered page for 10 minutes.
#     '''
#     response.headers['X-UA-Compatible'] = 'IE=Edge, chrome=1'
#     response.headers['Cache-Control'] = 'public, max-age=0'
#     return response


@app.route('/greyscale_citra',methods=['GET', 'POST'])
def convert_image():
    path_hasil = 'static/assets/greyscale_citra/hasil/'
    if request.method == 'POST':
        file = request.files['query_img']
        img = Image.open(file.stream)  # PIL image
        uploaded_img_path = 'static/assets/greyscale_citra/upload/'+ file.filename
        result_name = file.filename[:-4]
        img.save(uploaded_img_path)
        img_input = cv2.imread(uploaded_img_path)
        gray = cv2.cvtColor(img_input, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(path_hasil + result_name +'.jpg', gray)
        return render_template('greyscale_citra.html',query_path=uploaded_img_path,img=result_name)
    else:
        return render_template('greyscale_citra.html')


###########WAHYU
def plotting_model(weight, X, Y):
    plt.title('Prediksi Nilai Diabetes')
    plt.xlabel('Indeks Massa Tubuh')
    plt.ylabel('Nilai Diabetes')
    plt.plot(X, Y, 'k.')
    plt.grid(True)
    data = np.linspace(-0.2, 0.2, 10)
    for i in range(weight.shape[0]):
        y = weight[i, 0] + weight[i, 2] * data
        #print(y)
        plt.plot(data,y,'r-')
    y = weight[weight.shape[0] - 1, 0] + weight[weight.shape[0] - 1, 2] * data
    plt.plot(data,y,'b-')
    plt.savefig('static/assets/img/PlotLinReg.png')

@app.route('/task_linear_regression',methods=['GET', 'POST'])
def task_linear_regression_route():
    if request.method == 'POST':
        # Menyimpan nilai inputan dari web
        weight = 0
        mode = request.form['mode']
        # Training
        if mode == 'Training':
            epochs = int(request.form['query_epochs'])
            print(request.form.get('komposisi', None))
            test_size = (100 - int(request.form.get('komposisi'))) / 100
            option_show_training = request.form['query_tampil_training']
            data, target = load_diabetes(return_X_y=True)
            data_training, data_test, target_training, target_test = train_test_split(data, target, 
                test_size=test_size, random_state=0)
            stochasticGD = linearregressionmanual.ManualLinearRegression()
            weight = stochasticGD.training(data_training, target_training, epochs, 0.05)
            np.save('static/assets/model/model_linreg.npy', weight)
            weight = np.around(weight, decimals=2)
            num_of_weight, dim = weight.shape
            model = 'y = ' + str(round(weight[num_of_weight - 1][0], 2))
            for index_weight in range(1, dim):
                w = round(weight[num_of_weight - 1][index_weight], 2)
                model = model + (' + ' + str(w) + (' * x%s'%(index_weight)))
            # plotting_model(weight, data_training[:, 2], target_training)
            if option_show_training == 'Tidak':
                return render_template('task_linear_regression.html', model=model)
            elif option_show_training == 'Ya':
                return render_template('task_linear_regression.html', model=model, step_trains=weight, epochs=epochs)
        else:
            age = float(request.form['age_input'])
            sex = float(request.form['sex_input'])
            bmi = float(request.form['bmi_input'])
            bp = float(request.form['bp_input'])
            s1 = float(request.form['s1_input'])
            s2 = float(request.form['s2_input'])
            s3 = float(request.form['s3_input'])
            s4 = float(request.form['s4_input'])
            s5 = float(request.form['s5_input'])
            s6 = float(request.form['s6_input'])
            data_test = np.array([[age, sex, bmi, bp, s1, s2, s3, s4, s5, s6]])
            weight = np.load('static/assets/model/model_linreg.npy')
            stochasticGD = linearregressionmanual.ManualLinearRegression()
            predict = stochasticGD.testing(data_test, weight)
            predict = np.around(predict, decimals=2)
            return render_template('task_linear_regression.html', predict=predict[0])

    else:
        return render_template('task_linear_regression.html')


import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import normalize
@app.route('/task_logistic_linear', methods=['GET', 'POST'])
def task_logistic_regression_route():
    if request.method == 'POST':
        mode = request.form['mode']
        if mode == "Training":
            test_size = (100 - int(request.form['komposisi'])) / 100
            learning_rate = float(request.form['learning_rate'])
            epochs = int(request.form['query_epochs'])
            option_show_training = request.form['query_tampil_training']
            data, target = load_breast_cancer(return_X_y=True)
            data_training, data_test, target_training, target_test = train_test_split(data, target, 
                test_size=test_size, random_state=0)
            
            data_training = normalize(data_training)
            data_test = normalize(data_test)

            # Deklarasi objects
            logisticRegression = logisticregressionmanual.ManualLogisticRegression()
            weight = logisticRegression.training(data_training, target_training, epochs, learning_rate)
            np.save('static/assets/model/model_logreg.npy', weight)
            weight = np.around(weight, decimals=2)
            num_of_weight, dim = weight.shape
            model = 'y = ' + str(round(weight[num_of_weight - 1][0], 2))
            for index_weight in range(1, dim):
                w = round(weight[num_of_weight - 1][index_weight], 2)
                model = model + (' + ' + str(w) + (' * x%s'%(index_weight)))
            predict = logisticRegression.testing(data_test, weight[len(weight)-1])
            precision, recall = logisticRegression.accurate(target_test, predict)
            if option_show_training == 'Tidak':
                return render_template('task_logistic_regression.html', model=model, precision=precision, recall=recall)
            elif option_show_training == 'Ya':
                return render_template('task_logistic_regression.html', model=model, precision=precision, recall=recall, step_trains=weight, epochs=epochs)
        else:
            weight = np.load('static/assets/model/model_logreg.npy')
            test_from_input = request.form['input_test']
            print(test_from_input.split(','))
            default_test = np.array([[18.0, 10.3, 60.0, 1500.0, 0.08, 0.1, 0.1, 0.1, 0.1, 0.08, 1.0, 2.0, 10.0, 250.0, 
                0.02, 0.05, 0.1, 0.002, 0.04, 0.0015, 18.0, 25.0, 125.0, 2500.0, 0.1, 0.5, 0.712, 0.1, 0.3, 0.1]])
            temp_test = test_from_input.split(',')
            if len(temp_test) == 30:
                test = [[]]
                for i in range(30):
                    test[0].append(float(temp_test[i]))
                test = np.array(test)
            else:
                test = default_test
            # print(test.shape)
            logisticRegression = logisticregressionmanual.ManualLogisticRegression()
            predict = logisticRegression.testing(test, weight[len(weight)-1])
            # print(predict)
            if int(predict) == 0:
                kelas = 'Malignant'
            else:
                kelas = 'Benigh'
            return render_template('task_logistic_regression.html', kelas=kelas)
    else:
        return render_template('task_logistic_regression.html')


#----------BRIAN
# cart -----------------------------------------------------
from sklearn import datasets 
from sklearn.tree import DecisionTreeClassifier, export_text
import numpy as np
from sklearn.externals import joblib
from sklearn.model_selection import train_test_split
@app.route('/cart',methods=['GET', 'POST'])
def cart():
    path_hasil = 'static/assets/cart/hasil/'
    if request.method == 'POST':
        dataset = datasets.load_iris()
        
        komposisiTraining = int(request.form['komposisi'])
        komposisiTesting = (100 - komposisiTraining)/100
        
        X_train, X_test, y_train, y_test = train_test_split(dataset.data, dataset.target, test_size=komposisiTesting, random_state=0)        
        mode = request.form['mode']

        
        model_export_name = 'static/assets/model/model_cart.sav'
        if mode == 'training':
            decisionTreeClassifier = DecisionTreeClassifier(random_state=4)
            decisionTreeClassifier.fit(X_train, y_train)
            
            joblib.dump(decisionTreeClassifier, model_export_name)
            
            model = export_text(decisionTreeClassifier, feature_names=dataset['feature_names'])
            model = model.split('\n')
            for i in range(len(model)):
                model[i] = model[i]+'<br>'
            model = ''.join(model)
            model = model.split('   ')
            for i in range(len(model)):
                model[i] = model[i] + '&nbsp;&nbsp;&nbsp;&nbsp&nbsp;&nbsp;&nbsp;&nbsp&nbsp;&nbsp;&nbsp;&nbsp&nbsp;&nbsp;&nbsp;&nbsp'
            model = ''.join(model)

            akurasi = decisionTreeClassifier.score(X_test, y_test)
            
            return render_template('cart.html', mode='testing', komposisi=komposisiTraining, model=model, akurasi=akurasi)
        elif mode == 'testing':
            # sama seperti training, plus prediksi
            decisionTreeClassifier = joblib.load(model_export_name)

            model = export_text(decisionTreeClassifier, feature_names=dataset['feature_names'])
            model = model.split('\n')
            for i in range(len(model)):
                model[i] = model[i]+'<br>'
            model = ''.join(model)
            model = model.split('   ')
            for i in range(len(model)):
                model[i] = model[i] + '&nbsp;&nbsp;&nbsp;&nbsp&nbsp;&nbsp;&nbsp;&nbsp&nbsp;&nbsp;&nbsp;&nbsp&nbsp;&nbsp;&nbsp;&nbsp'
            model = ''.join(model)

            akurasi = decisionTreeClassifier.score(X_test, y_test)
            
            predictData = request.form['predictData']
            predictData = predictData.split(',')
            for i in range(len(predictData)):
                predictData[i] = float(predictData[i])
            
            predict = decisionTreeClassifier.predict([predictData])
            
            return render_template('cart.html', mode='testing', komposisi=komposisiTraining, model=model, akurasi=akurasi, prediksi=str(predict[0]))
    else:
        return render_template('cart.html', mode='training')
# ----------------------------------------------------------
# kmeans ---------------------------------------------------
from kmeans import Kmeans
from sklearn import datasets
from sklearn.model_selection import train_test_split
import numpy as np
@app.route('/kmeans',methods=['GET', 'POST'])
def kmeans():
    path_hasil = 'static/assets/kmeans/hasil/'
    if request.method == 'POST':
        file = request.files['query_img']
        img = Image.open(file.stream)  # PIL image
        uploaded_img_path = 'static/assets/kmeans/upload/'+ file.filename
        result_name = file.filename[:-4]
        img.save(uploaded_img_path)

        img_input = cv2.imread(uploaded_img_path)
        #img_input = cv2.resize(img_input, (128, 128))
        imgDim = img_input.shape
        img_input = img_input.reshape(imgDim[0]*imgDim[1],imgDim[2])
        
        epoch = int(request.form['epoch'])
        jumlahCluster = int(request.form['jumlahCluster'])
        centeroid = request.form['centeroid']
        if centeroid != "":
            centeroid = centeroid.split('-')
            if(jumlahCluster != len(centeroid)):
                return render_template('kmeans.html')

            for i in range(len(centeroid)):
                centeroid[i] = centeroid[i].split(',')
                for j in range(len(centeroid[i])):
                    centeroid[i][j] = int(centeroid[i][j])

            centeroid = np.array(centeroid)
            print('centeroid :\n', centeroid)
        else:
            centeroid = kmeans.findRandomCenter(img_input, 3)
        
        kmeans = Kmeans()

        result_paths = []
        predicts = []
        eDists = []
        centeroids = []
        for i in range(epoch):
            centeroid = kmeans.training(img_input, centeroid, 1)
            centeroids.append(centeroid)
            print('centeroid :\n', centeroid)
            predict, eDist = kmeans.predictEDist(img_input, centeroid)
            

            predict2img = kmeans.predict2img(predict, centeroid)
            predict2img = predict2img.reshape(imgDim)
            predict2img = np.array(predict2img, dtype=np.uint8)
            
            cv2.imwrite(path_hasil + result_name + str(i+1) + '.jpg', predict2img)
            result_paths.append(result_name + str(i+1) + '.jpg')

            predict, eDist = predict.reshape(imgDim[0]  , imgDim[1]), eDist.reshape(imgDim[0], imgDim[1])
            predict, eDist = np.array(predict, dtype=np.uint8), np.array(eDist, dtype=float)
            predict, eDist = cv2.resize(predict, (16, 16)), cv2.resize(eDist, (16, 16))
            predicts.append(predict)
            eDists.append(eDist)
            print(predict)

        print(result_paths)

        tampilProses = request.form.get('process')
        print(tampilProses)
        if tampilProses == 'yes':
            return render_template('kmeans.html', process='yes', query_img=file.filename, query_imgs=result_paths, centeroids=centeroids, predicts=predicts, eDists=eDists)
        else:
            return render_template('kmeans.html', process='no', query_img=file.filename, query_imgs=result_paths[-1], centeroids=centeroids[-1], predicts=predicts[-1], eDists=eDists[-1])
        
    else:
        return render_template('kmeans.html')
# ----------------------------------------------------------


if __name__ == "__main__":
    app.run(host="0.0.0.0")
