# Hybrid workflow of Simulation and Deep Learning on HPC: A Case Study for Material Behavior Determination

1 st Li Zhong *HLRS** Stuttgart, Germany li.zhong@hlrs.de

2 nd Dennis Hoppe *HLRS* Stuttgart, Germany dennis.hoppe@hlrs.de

3 th Naweiluo Zhou *HLRS* Stuttgart, Germany naweiluo.zhou@hlrs.de

4 th Oleksandr Shcherbakov *HLRS* Stuttgart, Germany oleksandr.shcherbakov@hlrs.de

*Abstract*—Nowadays, machine learning (ML), especially deep learning(DL) methods, provide ever more real-life solutions. However, the lack of training data is often a crucial issue for these learning algorithms, the performance accuracy of which relies on the amount and the quality of the available data. This is particularly true when applying ML/DL based methods for specific areas e.g. material characteristics identification, as it requires huge cost of time and manual power getting observational data from real life. In the mean while, simulations on HPC have already been commonly used in computational science due to the fact that it has the ability of generating sufficient and noise free data, which can be used for training the ML/DL based models. However, in order to achieve accurate simulation results the input parameters usually have to be determined and validated by a large number of tests. Furthermore, the evaluation and validation of such input parameters for the simulation often require a deep understanding of the domain specific knowledge, software and programming skills, which can in turn be solved by ML/DL based methods. In this paper, a novel hybrid workflow combining a multi-task neural network and the simulation on high performance computers(HPC) is proposed, which can address the problem of data sparsity and reduce the demand for expertise, resources, and time in determining the validated parameters for simulation. This work is demonstrated through experiments on determination of material behaviors, and the results prove a promising performance (MSE = 0.0386) through this workflow.

*Index Terms*—HPC, Simulation, Deep Learning, Workflow, Computational Materials Science

## I. INTRODUCTION

In the past decade, machine learning, specifically deep learning methods started to revolutionize several application domains. While deep learning has demonstrated strong abilities at extracting high-level representations of complex processes, the lack of sufficient ground truth data and is often a critical issue faced in various areas. In fact, it is almost impossible to generate enough data in real life for supervised learning in many real-world problems, which are limited by scientific instrument, physical phenomenon itself, or the complexity of modeling. Nowadays, different methods have been developed to solve this problem, e.g. transfer learning, data augmentation, usage of synthetic data, generation of new data through Generative Neural Networks(GAN), etc. Recently, scientists and engineers have begun experimenting with a relatively new approach to understand complex systems using ML predictive models, primarily Deep Neural Networks (DNNs), trained by the virtually unlimited data sets produced by simulations [23]. Studies have proven that these "synthesis models," combining ML and traditional simulation, can improve accuracy, accelerate time to solution and significantly reduce costs [24].

To perform simulations, input parameters have to be determined and validated by a large number of tests to expect accurate simulation results [1]. Furthermore, the evaluation and validation of such input parameters for the simulation often require a deep understanding of the domain specific knowledge, software and programming skills. Thus, how to efficiently define and validate the input parameters for the simulation becomes the key factor in the development and design of numerical models. While simulation can solve the data sparsity problem for DNN models, DL based methods can in turn solve the difficulty in determination and validation of the input parameters for simulation by training DNN models. However, both training of DNN model and the running of simulations are compute-intensive tasks, in which the supercomputers can manifest their computation efficiency.

This work contributes to the following aspects.

- We propose a novel hybrid workflow that combine a multi-task neural network and the simulation on HPC clusters with CPU and GPU support. This can address the problem of data sparsity and reduce the demand for expertise resources, and time in determining the validated parameters for simulation.
- We demonstrate the effectiveness of this workflow through an experiment of our design that can determine

698

<sup>*:</sup> High Performance Computing Center Stuttgart

This work has been supported by the project CATALYST, which is funded by the Ministry of Science, Research and Arts (MWK), Baden-Wurttemberg, ¨ Germany.

material behaviour. In the area of computational material science, to accurately determine material behaviours is always uneasy, as it costs significant amount of time and requires to manually get the observed data from real life.

- We perform the simulation using Finite Element Method (FEM) [10] and improve the simulation results by definition of input parameters through training of DNN models.
The rest of the paper is organized as follows. Section II reviews the most recent developments in DL aided simulation and learning on virtual data generated by simulations. In Section III, we describe the proposed method, which mainly focuses on the workflow design and the multi-task neural network design. Section IV presents the preliminary results and also reports the optimization methods. Finally, we conclude our paper and outlook the future work in Section V.

## II. RELATED WORK

Virutal data generated by simulations have been widely used for improving the performance of DNN models in various areas: education [26], medical [27], computational imaging [25], computational mechanics [28], climate modeling [29], etc. In the other way round, the ML/DL aided simulation has also developed very fast, many studies and researches have been done. Hu et al. [30] proposed a Long Short Memory (LSTM) network to help improve the simulation of rainfallrunoff, so that potential flood can be predicted. Yeo et al. [31] developed a DNN model, DE-LSTM, to model the nonlinear dynamics so as to be used for the simulation of stochastic processes. Other researches on ML/DL aided simulations have also been reported [32]–[34].

In the area of computational materials science, it is more and more common to train learning algorithms with such virtually generated data due to the fact that FEM simulation can provide as much noise-free data as required [11], [12]. Traditional methods e.g. finite element model updating (FEMU) [2], Virtual Field Method (VFM) [3], iDIC [4], etc. have been used for a long time to determine and validate the input parameters for FEM simulation. Recently, due to the swift development of machine learning especially deep learning, methods based on machine learning algorithms have also been developed . Gorji et al. [5] proposed a three hidden layer neural network model to reproduce the force-displacement curves of the tensile tests with a prediction accuracy around 93%. Koch et al. [6] designed a simple neural network model for the estimation of yield curve parameters with the data from a tensile test. Chheda et al. [7] proposed a neural network based method for predicting forming limit curves based on chemical composition and rolling process parameters of sheet metals. Mozaffar et al. [8] presented a recurrent neural network model to model the complicated path-dependent plasticity behavior, which demonstrated a very promising performance.

#### III. METHODOLOGY

In this part, we will discuss how the simulation and the DNN model for prediction are defined. As illustrated in Fig. 1, the proposed method is consisted of three phases: data generation phase, training phase and inverse phase. In the data generation phase, a set of material tests were simulated using a variety of material parameters as inputs and recorded the results of the simulation. In the second phase, a DNN model is trained with the simulation outputs as inputs and the material parameters which are simulation inputs as outputs. In the third phase, the prediction values and the real input values are compared to improve the DNN model and the simulation performance. Therefore, the FEM simulation can address the problem of data sparsity and the introduction of machine learning methods can reduce the high demand of expertise, furthermore, both the performance of simulation and DNN model are improved.

## *A. Simulation*

The Barlat-3 parameter model [18] was employed in the data generation phase for the FEM simulation. The input parameters for the model is well selected to be sure that the calculation effort is manageable and the generated data set contains sufficient information. Details of the selected finite element model can be obtained from [13].

## *B. Multi-Task Neural Network*

As the input parameters for the simulation are individual values and the prediction of such individual values can be regarded individual tasks, a multi-task neural network is proposed based on the fact that multi task learning (MTL) can help improve the performance by introducing an inductive bias, leveraging the domain-specific information [22], increasing the sample size, and focusing its attention on those features that actually matters. We design our network structure by hard parameter sharing, which is the most commonly used approach to MTL in neural networks that can greatly reduce the risk of overfitting [17]. The overall structure of the model is depicted in Fig.2. The whole network is composed of two main parts: the shared network and individual network for each parameter output. In the shared network, 1D CNN layer and max-pooling layers are used to extract the global features. When designing the part of individual network for each output, we found that for the outputs(MP1, MP2 and MP4), 1D CNN layers and max-pooling layers followed by two fully connected layers could give out best prediction performance, while for individual network of the outputs(MP3, MP5, MP6, MP7 and MP8), a more complicated network which have more convolution and max-pooling layers should be designed to better learn the features. This is also reflected in Fig.5, where the loss for the outputs(MP3, MP5, MP6, MP7 and MP8) are higher than for the outputs(MP1, MP2 and MP4) even with the more complicated network structure. In the mean while, Batch Normalization is employed here to stabilize the learning process and Dropout layers are used to avoid overfitting.

In terms of training the network, the primary loss function used is the Mean Squared Error between the between the real fieldy rand the predicted field yˆ.To train the networks,

![](_page_2_Figure_0.png)

Fig. 1. Hybrid workflow of simulation and distributed deep learning on HPC, through which both the performance of simulation and DNN model are improved

a weighted MSE is employed as the loss function. As the 8 outputs are weighted equally, the loss function is described as:

$$L=\sum_{1}^{N}\sum_{i=1}^{I}\frac{1}{I}(y_{i}-\hat{y_{i}})^{2}\tag{1}$$

where N denotes the number of outputs to be predicted.

IV. PERFORMANCE EVALUATION

## *A. Experiment Setup*

The FEM simulation was carried out on the HPC system Hawk (HPE Apollo) [14], which is a flagship supercomputer of the High-Performance Computing Center Stuttgart (HLRS) Due to the huge amount of train data and the model complexity, the DNN model was trained distributed on another GPU HPC system Vulcan(CS-Storm) [15], which serves as HLRS's primary machine to accelerate artificial intelligence (AI) workloads. The detailed technical specifications can be found in Table I. The two HPC systems use the common file system via a workspace mechanism [9], so that data can freely exchange between the two phases of the workflow.

## *B. Dataset*

The training database [19] was created using FEM simulations of tensile tests, which contains the values of the x-strains and in the second half the values of the y-strains. Each third of these halves refers to a specimen with 18 elements. For each element, 10 consecutive strain values from 10 time steps are taken. For each finite element, the longitudinal and transverse strains were exported for 10-time steps. A total of 1080 strain values were thus obtained per FE simulation, which means that each record of the FM simulation output is a 1080 size vector,

TABLE I TECHNICAL SPECIFICATION OF HAWK AND VULCAN

| System | HPE Apollo | Cray CS-Storm |
| --- | --- | --- |
| Number of compute nodes | 5632 | 8 |
| Peak performance | 26 Petaflops | 125 TFLOPS (tensor performance) |
| CPU/GPU type | AMD EPYCTM 7742 | Nvidia Tesla V100 SXM2 |
| Number of cores | 720,896 | 5120(CUDA cores) |
| CPU frequency | 2.25 GHz | - |
| Interconnect | InfiniBand HDR200 | InfiniBand HDR100 |
| Interconnect bandwidth | 200 Gbit/s | 300 Gbit/s |

and the total dataset is around 3 TB composed of 4,941,258 records, where train and test dataset are split from with a ratio (0.9,0.1). One record of the simulation output is as illustrated in Fig. 3, which can be regarded as a sequence of features from 6 dimensions coming in 10 time steps.

## *C. Result and Analysis*

In this section, we evaluate the performance of the model by inspecting the change of losses during training and testing it on the validation dataset. The losses of each output and as a whole during the training process are shown in Fig.5, the total training loss is around 0.0343 and the total validation loss is around 0.0386. The error histogram shown in Fig.4 indicates that the normalized maximum error of the values for outputs (MP4, MP5, MP6, MP7 and MP8) are about 0.2, whereas about 90 % of the errors are below 0.1. The maximum error of the values for outputs (MP1, MP2 and MP3) of the

![](_page_3_Figure_0.png)

Fig. 2. Architecture of the multi-task learning model, with sequence input and 8 dense values as output

![](_page_3_Figure_2.png)

Fig. 3. Visualization of the dataset generated by simulation, which contains the values of the x-strains and in the second half the values of the y-strains. Both x-strain and y-strain have 3 specimens and each specimen is composed of with 18 elements. For each element, 10 consecutive strain values from 10 time steps are taken

![](_page_3_Figure_4.png)

Fig. 4. Error histogram of the result on the test dataset

error histogram is only 0.02, whereas about 90 % of the errors are below 0.01. It was shown that the input material parameters for simulation can be approximated relatively well by our MTL model, and the performance of our MTL model keeps improving along with the increase of simulation data, which leads to the fact that both the simulation and DNN performance can be improved through such workflow.

## *D. Optimization*

As the whole dataset is around 3 TB and the DNN is trained on multiple nodes in a distributed manner, different optimization methods are required to improve the training performance, e.g. learning rate schedule, data I/O optimization, etc.

*1) Learning Rate Schedule:* In the training of DNN, most of the models use stochastic gradient descent (SGD) for optimization. It is usually difficult to decide a adequate learning rate, as a large learning rate will lead to overshooting loss minimum and a small learning rate will lead to a extremely slow convergence. Therefore, a well designed learning rate scheduler is gaining popularity in gradient based optimization, which has the ability of achieving optimal asymptotic convergence rate

![](_page_4_Figure_0.png)

Fig. 5. The total training loss is around 0.0343, and the validation loss is around 0.0386

and escaping from poor local minima [21]. Compared with static learning rate, a learning rate scheduler usually uses larger learning rate values at the beginning of the training procedure which makes large changes, and decreases the learning rate such that a smaller rate and therefore smaller training updates are made to weights later in the training procedure. In this work, a exponential decay sine wave learning rate [17] is applied, which scans a range of learning rate in each epoch and varies in sine wave way in the training process. The control of the learning rate is according to:

$$lr(t)=lr_{0}e^{\frac{-\alpha t}{T}}(sin(\beta\frac{t}{b2\pi})+e^{\frac{-\alpha t}{T}}+0.5)\tag{2}$$

where t is the number of epochs, lr0 is the initial learning rate, T denotes the total number of eopchs and b is the number of batches. α and β can control the decay and oscillation nature of the learning rate. So that the learning rate would vary in a sine way during the training process, while the maximum value of sine wave would decay exponentially along with training epochs.

*2) Distributed Strategy:* In order to take advantage of the great computation power provided by Vulcan, it is necessary to do the training distributedly. To achieve this goal, a data parallelism strategy is adopted, where the whole dataset is split into different batches and assigned to different GPUs. In the meanwhile, a replica of the model is created per GPU, each variable in the model is mirrored across all the replicas. All variables are synchronized by applying identical updates. As the code is implemented in Tensorflow 2, efficient all-reduce algorithms implemented in NVIDIA Collective Communication Library(NCCL) are used to do the communication across all GPUs which can reduce the overhead of the synchronization significantly.

*3) Data Pipeline Optimization:* As is shown in Fig.6, input pipeline of dataset from file system takes the longest to execute during the whole training process. The input pipeline performs actual I/O, decoding and pre-processing, among which the read and pre-process take the longest to execute. Thus, to achieve the peak performance, it is necessary to implement

an efficient input pipeline, especially a efficient read and preprocess, that delivers data for the next step before the current step has finished. The common approach is to optimize this process by overlapping the input pipeline with the computation pipeline [20]. In this work, further optimization methods have been adopted:

- Parallel I/O: Input files are read and pre-processed individually with individual outputs as a embarrassingly parallel process. The parallelization of the I/O of many files (343 in our case) can be done by mapping the list of the file names for transformation. The I/O will be executed by threads that are spawned by the runtime, where the number of threads is specified manually.
- Prefetching: Prefetch is used here to ensure there will be a specified number of batches ready for the consumption, where the data from the previous pipeline is 'prefetched'. The prefetcher runs as a background thread and a consumption function, which contains an infinite loop waiting for a condition variable.
- Caching: The cache of data in memory or on local storage can save some of the operations like file opening and data reading from being executed during training. By applying the cache method, the transformations before the cached one are executed only during the first epoch, the following epochs will reuse the data cached.

The comparison of execution time between the training before optimization and after optimization is shown in Fig.7. As can be seen that, by applying the optimization methods listed above, the execution time of the whole process is decreased from around 179 minutes on 1 GPU, 25 mintutes on 32 GPUs to 35 minutes on 1 GPU and 40 seconds on 32 GPUs.

## V. CONCLUSION AND OUTLOOK

In this paper, we have investigated and proposed a hybrid workflow composed of a FEM simulation and a DNN model on HPC. For the FEM simulation, the Barlat-3 parameter model was adopted to generate virtual data. Afterwards, the

![](_page_5_Figure_0.png)

(a) Time consumption of each step during training (b) Time consumption when reading from shared file system

![](_page_5_Figure_3.png)

![](_page_5_Figure_4.png)

![](_page_5_Figure_5.png)

simulation outputs would then be fed as inputs to the DNN model which can predict the simulation input parameters in return. The DNN model was designed with a multi-task network architecture and scaled to multi nodes to accelerate the training. In order to improve the performance, several optimization methods were also discussed here. The experiments conducted successfully proves that the performance of the simulation and the DNN model can be improve by such workflow.

In the future work, we will focus on improving the performance of the neural network, especially when scaling on HPC environment. In addition, further studies are required to bridge the gap between the expertise of mechanics and machine learning through the methods of AutoML, so that the requirement of knowledge on machine learning and deep learning will be eliminated.

## ACKNOWLEDGMENT

We would like to show our appreciation to Dr. Celalettin Karadogan and Mr. Patrick Cyron from the Institute for Metal Forming Technology of University of Stuttgart for providing the dataset for our experiment.

## REFERENCES

- [1] Abspoel, M., Scholting, M. E., Lansbergen, M., An, Y., & Vegter, H. (2017). A new method for predicting advanced yield criteria input parameters from mechanical properties. Journal of Materials Processing Technology, 248, 161-177.
- [2] Kajberg, J., & Lindkvist, G. (2004). Characterisation of materials subjected to large strains by inverse modelling based on in-plane displacement fields. International Journal of Solids and Structures, 41(13), 3439-3459.
- [3] Pierron, F., & Grediac, M. (2012). The virtual fields method: extracting ´ constitutive mechanical parameters from full-field deformation measurements. Springer Science & Business Media.
- [4] Mathieu, F., Leclerc, H., Hild, F., & Roux, S. (2015). Estimation of elastoplastic parameters via weighted FEMU and integrated-DIC. Experimental Mechanics, 55(1), 105-119.
- [5] Gorji, M. B., & Mohr, D. (2019, November). Towards neural network models for describing the large deformation behavior of sheet metal. In IOP Conference Series: Materials Science and Engineering (Vol. 651, No. 1, p. 012102). IOP Publishing.
- [6] Koch D and Haufe A, 2019, An investigation of machine learning capabilities to identify consti-tutive parameters in yield curves. International Deep Drawing Research Group 2019, Enschede/ Netherlands
- [7] Chheda, A. M., Nazro, L., Sen, F. G., & Hegadekatte, V. (2019, November). Prediction of forming limit diagrams using machine learning. In IOP Conference Series: Materials Science and Engineering (Vol. 651, No. 1, p. 012107). IOP Publishing.
- [8] Mozaffar, M., Bostanabad, R., Chen, W., Ehmann, K., Cao, J., & Bessa, M. A. (2019). Deep learning predicts path-dependent plasticity. Proceedings of the National Academy of Sciences, 116(52), 26414- 26420.
- [9] hpc-workspace. Retrieved July 4, 2021 https://github.com/holgerBerger/hpc-workspace
- [10] K.-J. Bathe,Finite element method. Wiley Online Library, 2008.
- [11] Lorente, D., Mart´ınez-Mart´ınez, F., Ruperez, M. J., Lago, M. A., ´ Mart´ınez-Sober, M., Escandell-Montero, P., ... & Mart´ın-Guerrero, J. D. (2017). A framework for modelling the biomechanical behaviour of the human liver during breathing in real time using machine learning. Expert Systems with Applications, 71, 342-357.
- [12] Luo, R., Shao, T., Wang, H., Xu, W., Zhou, K., & Yang, Y. (2018). Deepwarp: Dnn-based nonlinear deformation. arXiv preprint arXiv:1803.09109
- [13] Guner, A., Soyarslan, C., Brosius, A., & Tekkaya, A. E. (2012). Charac- ¨ terization of anisotropy of sheet metals employing inhomogeneous strain fields for Yld2000-2D yield function. International Journal of Solids and Structures, 49(25), 3517-3527.
- [14] HLRS 2020.HAWK Supercomputer. Retrieved July 4, 2021 from https://www.hlrs.de/systems/hpe-apollo-hawk/
- [15] HLRS 2021.NEC Cluster (Vulcan). Retrieved July 6, 2021 from https://www.hlrs.de/systems/nec-cluster-vulcan/
- [16] Crawshaw, M. (2020). Multi-task learning with deep neural networks: A survey. arXiv preprint arXiv:2009.09796.

- [17] An, W., Wang, H., Zhang, Y., & Dai, Q. (2017, December). Exponential decay sine wave learning rate for fast deep neural network training. In 2017 IEEE Visual Communications and Image Processing (VCIP) (pp. 1-4). IEEE.
- [18] Barlat, F., Aretz, H., Yoon, J. W., Karabin, M. E., Brem, J. C., & Dick, R. E. (2005). Linear transfomation-based anisotropic yield functions. International Journal of Plasticity, 21(5), 1009-1039.
- [19] Karadogan, C., Cyron, P., & Liewald, M. (2021, June). Potential use of machine learning to determine yield locus parameters. In IOP Conference Series: Materials Science and Engineering (Vol. 1157, No. 1, p. 012064). IOP Publishing.
- [20] Chien, S. W., Markidis, S., Sishtla, C. P., Santos, L., Herman, P., Narasimhamurthy, S., & Laure, E. (2018, November). Characterizing deep-learning I/O workloads in TensorFlow. In 2018 IEEE/ACM 3rd International Workshop on Parallel Data Storage & Data Intensive Scalable Computing Systems (PDSW-DISCS) (pp. 54-63). IEEE.
- [21] Darken, C., Chang, J., & Moody, J. (1992, August). Learning rate schedules for faster stochastic gradient search. In Neural networks for signal processing (Vol. 2).
- [22] Caruana, R. (1998). Multitask learning. autonomous agents and multiagent systems.
- [23] Kadupitige, K. (2017). Intersection of hpc and machine learning. Digital Science Center.
- [24] Kerestely, ´ A. (2020). HIGH PERFORMANCE COMPUTING FOR ´ MACHINE LEARNING. Bulletin of the Transilvania University of Brasov. Mathematics, Informatics, Physics. Series III, 13(2), 705-714.
- [25] Fei Wang, Hao Wang, Haichao Wang, Guowei Li, and Guohai Situ, "Learning from simulation: An end-to-end deep-learning approach for computational ghost imaging," Opt. Express 27, 25560-25572 (2019)
- [26] Jadhao, V., & Kadupitiya, J. C. S. (2020, November). Integrating machine learning with hpc-driven simulations for enhanced student learning. In 2020 IEEE/ACM Workshop on Education for High-Performance Computing (EduHPC) (pp. 25-34). IEEE.
- [27] Sekh, A. A., Opstad, I. S., Agarwal, R., Birgisdottir, A. B., Myrmel, T., Ahluwalia, B. S., ... & Prasad, D. K. (2020). Simulation-supervised deep learning for analysing organelles states and behaviour in living cells. arXiv preprint arXiv:2008.12617.
- [28] Hamrick, J. B. (2019). Analogues of mental simulation and imagination in deep learning. Current Opinion in Behavioral Sciences, 29, 8-16.
- [29] Partee, S., Ellis, M., Rigazzi, A., Bachman, S., Marques, G., Shao, A., & Robbins, B. (2021). Using Machine Learning at Scale in HPC Simulations with SmartSim: An Application to Ocean Climate Modeling. arXiv preprint arXiv:2104.09355.
- [30] Hu, C., Wu, Q., Li, H., Jian, S., Li, N., & Lou, Z. (2018). Deep learning with a long short-term memory networks approach for rainfall-runoff simulation. Water, 10(11), 1543.
- [31] Yeo, K., & Melnyk, I. (2019). Deep learning algorithm for datadriven simulation of noisy dynamical system. Journal of Computational Physics, 376, 1212-1231.
- [32] Othman, M. S. B., & Tan, G. (2018, October). Machine learning aided simulation of public transport utilization. In 2018 IEEE/ACM 22nd International Symposium on Distributed Simulation and Real Time Applications (DS-RT) (pp. 1-2). IEEE.
- [33] Worrlein, B., Bergmann, S., Feldkamp, N., Straßburger, S., Putz, M., ¨ & Schlegel, A. (2019). Deep-Learning-basierte Prognose von Stromverbrauch fur die hybride Simulation. Simulation in Produktion und Logis- ¨ tik 2019, 121-131.
- [34] Moseley, B., Markham, A., & Nissen-Meyer, T. (2018). Fast approximate simulation of seismic waves with deep learning. arXiv preprint arXiv:1807.06873.

