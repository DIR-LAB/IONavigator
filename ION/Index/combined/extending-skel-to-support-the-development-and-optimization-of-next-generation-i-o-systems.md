# Extending Skel to support the development and optimization of next generation I/O systems

Jeremy Logan, Jong Youl Choi, Matthew Wolf, George Ostrouchov, Lipeng Wan, Norbert Podhorszki, William Godoy and Scott Klasky Oak Ridge National Laboratory Oak Ridge, TN, USA

Erich Lohrmann and Greg Eisenhauer Georgia Institute of Technology Atlanta, GA, USA

Chad Wood and Kevin Huck University of Oregon Eugene, OR, USA

*Abstract*—As the memory and storage hierarchy get deeper and more complex, it is important to have new benchmarks and evaluation tools that allow us to explore the emerging middleware solutions to use this hierarchy. Skel is a tool aimed at automating and refining this process of studying HPC I/O performance. It works by generating application I/O kernel/benchmarks as determined by a domain-specific model. This paper provides some techniques for extending Skel to address new situations and to answer new research questions. For example, we document use cases as diverse as using Skel to troubleshoot I/O performance issues for remote users, refining an I/O system model, and facilitating the development and testing of a mechanism for runtime monitoring and performance analytics. We also discuss dataoriented extensions to Skel to support the study of compression techniques for Exascale scientific data management.

#### I. INTRODUCTION

As high performance computing hardware has continued to evolve and improve, many of the ratios between FLOPS, memory, bandwidths, and I/O that were used as design parameters in the past have changed significantly. In particular, the exponential increase in capacities (compute or storage) has not been met by a similar increase in bandwidths, with the practical result that much work at the extreme scale is devoted to understanding how to keep all of the compute resources "fed", and there is a particular set of challenges around both read and write I/O performance that emerges at these scales. At the simplest level of accounting, such unoptimized I/O reduces the amount of science that can be delivered despite the large investment in leadership computing environments.

To complicate matters, applications have reacted to the riches of 100+PetaFlop environments by looking at new algorithmic designs: explicit ensemble management, multi-physics code-coupling, or simulation-experiment interactions. At an even lower-level, the rise of interest in task-driven models like OCR, DIY, or Legion cause a much more asynchronous I/O pattern than traditional approaches expect. Further driving the problem, the increasing size of data is leading to greater need to integrate data compression and reduction techniques into these workflows. To meet these needs, new I/O and storage systems are being developed that must be evaluated using realistic workloads, and we must be able to cast those workloads across new and existing platforms.

A fundamental issue with this, however, is that the Computer Science community, and particularly the I/O research contingent, is lacking for easy proxies and models that can exhibit some of these behaviors. Static I/O benchmarks [27], [26], [31] typically lack the flexibility that is needed to address the many requirements of current I/O research and development. Other work [30] done in the context of resilience has highlighted the need to match the exhibited behaviors of your benchmark or proxy to the real features of the original applications at scale.

Skel [20] is a tool that we have been using to address some of these challenges. Skel generates I/O "skeletons", utilizing a model for the application derived from the properties of its regular diagnostic and/or checkpoint output that have been written using the ADIOS [19] Adaptable I/O System. As we will show through several distinct use cases, by focusing on building appropriate I/O-focused models of the parallel scientific code, the Skel tool environment makes it easy to extend the skeleton with additional run-time or data properties to enable the type of feature-preserving proxies that are needed for advanced I/O research.

Further, because the modifications are done at the model level, Skel opens up a new mode of collaboration with end users, as they can utilize the skel tools to generate the model and only ship that (and perhaps some representative data) to an I/O researcher as a start to working on performance understanding and tuning of the code. For science codes with large code bases and complex build dependencies, this can make rapid prototyping, exploration of I/O alternatives, and community adoption of use cases feasible in a way that was not true before.

In the remainder of this paper, we present an overview of the technologies and capabilities associated with Skel. We then follow up with four distinct case studies that explore how Skel has enabled performance tuning, I/O investigations, or complex in situ research for systems that were not well represented by traditional I/O benchmarks. We will then conclude with some remarks on future work and research directions that can be enabled with the Skel environment.

2168-9253/17 $31.00 © 2017 IEEE DOI 10.1109/CLUSTER.2017.30

# II. SKEL: A GENERATIVE TOOL FOR EXPLORING APPLICATION PERFORMANCE AT SCALE

Skel is a generative tool that was originally developed to produce simple I/O benchmark codes. The simplicity of these codes contrasts with the relatively complex process of building and running many scientific simulation codes, which often have a set of library dependencies, a complex build mechanism, and require a non-trivial input deck just to exercise the I/O features of the code. I/O kernels built by hand can also overcome this complexity, but require programmer time and effort, and must be kept up to date with application changes. Skel offers a model-driven approach to automatically generate useful benchmark codes, as well as a mechanism to adjust the code that is generated to fit the rapidly changing needs of I/O research.

# *A. Skel Design*

Skel uses a high-level model to describe an application's I/O behavior, which is used to generate benchmark codes and other artifacts that implement instances of the model. A skel model consists minimally of the names, types, and sizes of variables to be written (which together form an Adios group). As there are things beyond simple byte transfer that affect I/O performance, the model is flexible enough to allow extensions such as information about the frequency of I/O operations, transport method and associated parameters used for writing, transformations to be applied to the data, etc.

The skel tool accepts these I/O models as input to code generators that produce components of a mini-app that exercises the I/O described in the model. Skel's original code generation strategy is illustrated in Fig. 1.

![](_page_1_Figure_5.png)

Fig. 1. The Skel source-generation pattern. Skel takes an I/O model as input and produces a skeletal application that reflects the model.

We have added a new capability, known as skel replay, to the Skel utility in an effort to simplify the process of recreating an I/O behavior of an existing application. The replay mechanism works in conjunction with the skeldump utility, which extracts metadata contained in an Adios BP file and uses it to create a skel model with little user input. Use of this model allows users to automatically replay the I/O behavior that produced the output file. This process is illustrated in Fig. 2. An output file from the application of interest is processed by skeldump to produce a yaml file describing the application's I/O behavior. The yaml file is then provided as input to skel replay to produce a benchmark code that mimics the I/O behavior of the application. Use of skeldump and skel replay is discussed in more detail in Section III.

## *B. Skel Implementation*

Skel provides several mechanisms for representing I/O models. A model can be produced from the XML descriptor

![](_page_1_Figure_10.png)

Fig. 2. Use of skeldump and skel replay. Skeldump extracts an I/O model from an Adios output file. The I/O model is then provided as input to skel replay, which produces a skeletal application for that model.

that is typically used by many applications that use Adios [21]. In addition to the XML representation, Skel also accepts a YAML representation of the I/O model, which provides slightly different features than the XML descriptor.

Skel leverages several different strategies to generate codes. In the first of these strategies, *direct emitting*, code in the target language is embedded into the skel code as text strings and written directly to an output file by the generator code. The main drawback with this approach is that it quickly becomes difficult to maintain as complexity is added to the model. With more options, the tree of conditional branches required to emit appropriate outputs grows, and related code fragments become widely separated, making the logic of the generator code is difficult to follow.

A second technique used by skel is the *simple template* approach that allows boilerplate target code to be placed into a separate file. The simple template engine processes this file, inserting dynamic code snippets at tagged locations to produce the target code. This simplifies the generative code compared to direct emitting, but still requires the replacement items to live in the generative code, which means providing a different piece of code for each tag in the target file. The main drawback with this approach is that the generative content is split between a template and the shared generator code, causing the generator code to become unweildy as more targets are added.

The third code generation mechanism leverages an existing template instantiation library, Cheetah [7], to provide a more powerful template mechanism including not only simple string replacement, but also loops and conditionals, allowing simple generation of codes with arbitrary lists of variables while using a simpler, target agnostic code generation engine that does not need to be modified as more targets are added. This technique offers the advantage of a clean separation between the generator code and the content being generated.

All three types of code generation are currently present in the Skel code. We are gradually phasing out targets that use the first two approaches in favor of the Cheetah-based code generation.

Initially, the details of the internal code generation techniques had little impact on the user's experience, but with the advent of templates, we now have the ability to expose the templates used for the generation process to the users, allowing those templates to be modified to fit a user's requirements. This is a powerful mechanism becuase it allows users to make adjustments that impact all of the generated mini-applications, avoiding the situation where minor adjustments need to be made manually to a large set of similar generated codes.

The ability to adjust existing templates is used for targets

already known to Skel, such as benchmark source codes and Makefiles, but there are times when it is convenient to create an entirely different type of output from an ad hoc model. To allow this flexibility, we have also provided skel template, which takes a user-provided template, and a model expressed as a YAML file, and produces an arbitrary output file.

In the following sections we provide a collection of case studies that illustrate the use of the tool and show some of the optimization we have performed with it.

## III. CASE STUDY: USER SUPPORT WORKFLOW FOR ADIOS

![](_page_2_Figure_3.png)

Fig. 3. Using skel replay to troubleshoot performance issues in Adios.

It is common for Adios users to contact us with concerns about the performance of their code during a particular run. Generally, these questions are difficult to answer, as recreating the user's situation involves duplicating the I/O behavior of the application in question, at the particular scale at which they ran, and on the same platform, to which we may not have access. Even if we do have access, and are able to run their code directly, to gain insight into the performance characteristics of the code, it would be necessary to apply some instrumentation to the code to glean understanding of the nature and cause of the performance issue.

We have leveraged skel to address these types of situations in a straightforward manner. By using the skeldump tool, a user can extract information about an application's I/O behavior directly from the output files. This metadata, which is typically much smaller than the output data, can be transferred to the Adios developers, and then passed to skel replay to generate a skeletal mini-application that mimics the I/O behavior of the original application. Fig. 3 illustrates this use of skel replay to troubleshoot an Adios user's performance issue.

To gain more insight into the nature of observed performance issues, we have also extended the templates used to generate the mini-application's makefile so that the executable is linked with a tracing tool such as Score-P or VampirTrace. This results in a trace file being generated during the execution of the mini-application that can subsequently be visualized with Vampir, [24] producing a very detailed picture of how time is used within the mini-app, and more specifically, within the I/O calls.

![](_page_2_Figure_9.png)

Fig. 4. Score-P traces of the skel application visualized in Vampir, showing a) undesired serialization of POSIX open calls inside Adios, and b) improved behavior after applying a fix for the performance bug.

For example, we were recently contacted by the user of a physics simulation code who observed that when a similar I/O phase was performed repeatedly over the runtime of the code, the first iteration of that I/O took significantly longer than subsequent iterations. Using the skeldump file provided by the user, we created a mini-app, and ran it locally to reproduce the problem. A visualization of one execution of the mini-app is shown in Fig. 4a. Sections designated by the letters A-D correspond to the POSIX open calls made in each of four iterations of the I/O cycle. We were able to quickly determine that the stair-step pattern shown in section A corresponded to undesirable serialization of file open operations across nodes. We traced this to some buggy code that had been introduced to slow down the open operations for highly parallel codes to avoid overwhelming the file system's metadata server. After a fix was applied to Adios, a subsequent run of the mini-app produced the trace shown in Fig. 4b, where it can be seen that this serialization problem has been eliminated.

## IV. CASE STUDY: SYSTEM MODELING

Understanding I/O performance on high performance infrastructures, from the department-level cluster to a leadershipclass supercomputer, can be very complex. The interplay between various hardware and software layers makes it hard to predict where the bottlenecks in the distributed system are, even if you're talking about a single-user scenario. In practice, most such machines support mulptile users, and that causes a level of dynamism in user-perceived throughput that makes it hard to plan around; measured I/O performance at some of

![](_page_3_Figure_0.png)

Fig. 5. Support for system I/O performance modeling.

the most well-tuned leadership computing facilities has shown periodic fluctuations in available I/O bandwidth of more than an order of magnitude.

As such, direct probing measurements of the I/O performance of large-scale runs of scientific applications would allow both application developers and system administrators to understand the characteristics and variability of the parallel I/O in HPC storage systems. However, in practice, the large-scale I/O performance measurements are not always feasible, since running such measurements themselves can cause significant performance degradation in the production environment. The approach being followed by this project [29] is to enhance techniques for predicting I/O performance in real time, taking into account both native hardware capabilities and the dynamic interference from other users. One approach to making these predictions is to create a performance model that captures the I/O characteristics of the storage system. Such a model allows us to estimate the I/O performance of different scientific applications without launching large-scale measurements on real HPC systems.

The initial work proceeded using a specifically tuned performance sampling infrastructure that used a number of approaches to get at the raw available hardware bandwidth, such as turning off all user-side caching of data. Such measurements are important to assess how other users affect the available I/O capacity at a fundamental level. However, this sampling approach by itself is therefore too simplistic to capture the full dynamics that involve caching and internal application interference effects. By coupling the systemic performance sampling techniques with a Skel-generated I/O benchmark, we believe we can generate data sets that will allow us to correctly parameterize a much more accurate predictive model.

Figure 5 illustrates how we are leveraging Skel to design, parameterize and use such an I/O performance model. First of all, designing the model requires prior knowledge of the system I/O characteristics which we are capturing by running the skeletal applications generated by Skel. Using the skeletal applications to test I/O performance allows us to mimic the I/O behavior of a variety of applications with significantly less overhead than using the applications themselves. Once the I/O measurements have been collected, they are then used to train the system I/O performance model to find the optimal parameter setting for such model.

![](_page_3_Figure_6.png)

Fig. 6. An example of the discrepancy between the hardware prediction model without cache effects and the throughput measurements when skel can take all application and caching effects into account.

#### *A. Modeling Exascale Application I/O*

As a concrete demonstration of this further extension to the modeling work, let us consider performance of XGC1 running on Titan at the Oak Ridge Leadership Computing Facility. XGC1 [6] is a core component of the Whole Device Modeling fusion simulation within the Exascale Computing Project [11]. As such, being able to predict the I/O performance and variability can be a significant help in understanding how to tune the code to achieve proper balance of performance across compute and I/O at the extreme scale. In our on-going study, we have developed a runtime I/O monitoring tool which can be integrated into those scientific simulation applications and periodically measure the end-to-end I/O latency. The measuring results help us build a hidden Markov model to characterize the end-to-end I/O performance in Titan's Lustre file system. With such model, the applications can estimate and predict the busyness of the storage system so that they can refactor and rearrange their I/O more efficiently.

Since our model focuses on the characteristics of the endto-end I/O performance, it does not take the caching effect into account. However, the usage of system cache in largescale computing facilities indeed has significant impact on the application-perceived I/O performance. Here we present a simple example to show why only using our end-to-end performance model is not enough to characterize the actual I/O performance at the application level. We run both the XGC1 and the I/O miniapp of XGC1 generated by Skel on Titan and let them write the data to the same group of OSTs. Meanwhile, we also launch the runtime I/O monitoring tool on each compute node to collect the end-to-end performance numbers and train the model. In Figure 6, we compare the predicted bandwidth of write requests issued to OST-0 on Titan during the running of a 64-node XGC1 job given by our model with the actual write bandwidth measured within XGC1 and the I/O miniapp. From the figure, we can observe that the predicted write performance is lower than the performance the application has actually perceived as our model excludes the effect of system cache. Skel can mimic an application's I/O behavior well and achieve a much closer approximation of the application's I/O performance. Therefore, Skel is a valuable complement to the end-to-end I/O performance model and can be leveraged to better characterize and understand

#### TABLE I

RELATIVE COMPRESSION SIZE OF XGC DATA WITH SZ AND ZFP AT DIFFERENT TIMESTEPS AND THEIR CORRESPONDING HURST EXPONENTS.

|  | Time step | Time step | Time step | Time step |
| --- | --- | --- | --- | --- |
| Algorithm | 1000 | 3000 | 5000 | 7000 |
| SZ (abs error: 1e-3) | 7.76% | 8.31% | 9.15% | 9.51% |
| SZ (abs error: 1e-6) | 16.38% | 17.54% | 19.03% | 20.58% |
| ZFP (accuracy: 1e-3) | 10.09% | 10.62% | 11.60% | 11.92% |
| ZFP (accuracy: 1e-6) | 16.48% | 17.01% | 17.99% | 18.30% |
| Hurst exponent | 0.71 | 0.30 | 0.77 | 0.83 |

(Relative compression size = compressed/uncompressed*100)

the I/O performance in exascale computing systems from the perspective of applications.

## V. CASE STUDY: ONLINE COMPRESSION METHODS

Testing workflows that utilize compression techniques presents an additional challenge compared to testing those without. Since the time and size performance of the compression and decompression routines will in many cases depend on the characteristics of the data being compressed, it is essential to use data that resembles that which is produced by an application of interest to test our compression techniques.

We are investigating two different strategies for providing more realistic data for I/O benchmarking. One such strategy is to leverage some actual output data from an application of interest. This "canned" data provides a direct measure of how a particular compression routine will behave, at least for particular runs of the application.

The second strategy we are pursuing is the generation of synthetic data sets. Generated data sets would have three main advantages, 1) We would be able to incorporate a larger range of outputs simply by measuring a small parameter set for interesting variations of application runs. 2) We would have a viable benchmarking strategy for cases where the application data is not public, and sharing a canned data set is not an option, and 3) We avoid the need to transmit large data sets to new platforms of interest, since we could generate the synthetic data on the new platform on the fly.

#### *A. Using canned application data*

To address this need, and allow the examination of new compression algorithms, we have extended the standard skel template in two ways. First, we have extended the skel replay mechanism to use not only the metadata from an existing run of our application of interest, but also to use the data itself. So the skeletal application will read data from a given bp file, and then use that data in the timed writes. Secondly, we have extended the generated skeletal application to use a specified compression routine to compress data before using Adios to write. This allows us to both rapidly prototype new compression techniques directly in skel, and to use compression transformations available in Adios.

For example, Fig. 7 shows data from four time steps of an XGC simulation. XGC is a large-scale particle-in-cell (PIC)

![](_page_4_Figure_12.png)

based fusion simulation code that runs on DOE leadership computing facilities in the United States. The illustrated density potential field progressively moves from a static regime (Fig. 7a) to regimes where particles form turbulent eddies (Fig. 7d). This shows that the characteristics of data change as the XGC simulation proceeds. The early data (Fig. 7a) shows only small variability, while data getting close to the last time steps (Fig. 7d) shows very high variability and large turbulence. The data compression characteristics (such as quality, speed, predictability, etc.) vary at different timesteps. To illustrate the impact of data characteristics on compression quality, in Table I, we have applied SZ [8] and ZFP [18] compression techniques and compared the size of compressed data for the four XGC time steps. It can be observed that the compression results vary across the time steps for each of the compression techniques. Furthermore, the stability of the compression techniques varies for different techniques and different levels of accuracy. Thus it is essential that we consider the nature of an application's data in testing performance of workflows that use compression techniques

## *B. Generating useful data*

To drive the generation of synthetic data sets, we first want to characterize data with parameters that have a predictive capability for compressibility and that specify a data generation process. The Hurst exponent [15] is a potential candidate. It is sometimes used to measures long range persistence in growth increments of a series (for example in finance [2]). An asymptotic characteristic is that under independence, the Hurst exponent is 0.5 regardless of the original data distribution for a weakly stationary series (stable mean and variance) [12]. Values in (0.5, 1] indicate persistence and values in [0, 0.5) indicate anti-persistence, with 0.5 indicating independent series increments. However, visually, data with lower Hurst values display more roughness.

More importantly, the Hurst exponent is used as a parameter for a class of fractal stochastic processes called fractional Brownian motion [22], which are used for artificial series and terrain generation. Such terrain simulators range from those that generate landscapes with theoretically fractal structure, called *fractional Brownian process* (FBP) [3], [9] to various faster approximations. The FBP simulations are indexed by the Hurst exponent describing the roughness of the fractal landscape, which we expect to be related to compression performance. Figure 81 shows an example of an FBP surface for three values of the Hurst exponent.

Software is available for generating FBP data, for example [23], [4]. Simulating the surfaces in Fig. 8 can be computationally demanding but one dimensional series are much cheaper. We use such one dimensional FBP simulation in a small experiment to illustrate that compressibility can be controlled with the Hurst exponent. We computed Hurst exponents estimates from the XGC data shown in Fig. 7 and report them in the last line of Table I. Then, we used FBM software to generate a synthetic series of the same length. Fig. 9 shows

![](_page_5_Figure_8.png)

Fig. 8. Three examples of fractional Brownian surface based on three values of the Hurst exponent.

![](_page_5_Figure_10.png)

Fig. 9. Comparing data compression performance with real XGC data and synthetic data generated by fractional Brownian process. Synthetic data has been generated based on the estimated Hurst exponents of the XGC data at timestep 1000, 3000, 5000, and 7000 (shown in Table I). Compressed data sizes also remain between the randomly generated random (yellow line) and constant data (dark green).

compression performance on the original XGC data compared to the synthetic data with the same Hurst exponent. The other two lines, random and constant, are included to show bounds on the compression performance. We see that the Hurst exponent can control compression performance, with higher values giving greater compression. But clearly more work is needed to explore the relationship of compression performance between the synthetic and real data. We used a simple estimator of the exponent across the entire series, likely violating the weak stationarity implicit assumption. A better approach might explore more local estimation and control in future work. But our results already satisfy the more modest goal of controlling compression performance and specifying a data generation process.

## VI. CASE STUDY: MEASUREMENT OF IN SITU ANALYTICS

As we look toward exascale-capable infrastructures, both hardware and software, a common theme emerges. The ability to generate new scientific data steps far outstripts the I/O bandwidth available to save them; the ratio of floating point operations to I/O bandwidth is expected to decrease by more than an order of magnitude compared to today, and codes are already struggling. As a result, there has a been a renewed interest in online, in situ processing of data so that key features and elements can be preserved for future detailed analysis.

Against this background, though, is the complexity of planning out how best to deploy such combinations of codes at scale: a particular physics model might scale to 100k cores, but that does not mean that the scientists's preferred spectralbased analysis method would. That has led some to begin ernestly investigating multi-executable concurrent processing

<sup>1</sup>By Adamalgorithm (Using Matlab)

<sup>[</sup>GFDL (http://www.gnu.org/copyleft/fdl.html) or CC BY-SA 3.0

<sup>(</sup>http://creativecommons.org/licenses/by-sa/3.0)], via Wikimedia Commons

of data, streaming the raw data into parallel components that can manage that data. [33], [10]. This, however, brings about the possibility of a number of complex interactions, as these separately launched components could interfere with one another in memory contention, memory bandwidth, interconnect bandwidth, GPU utilization, and so on. Developing consistent benchmarking codes that can allow for the creation of different tools to assess and control the impact of such interference is an important step in building a broader community engagement in the topic.

## *A. Benchmarking for Monitoring Analytics*

The MONA, or MONitoring Analytics, project [17] is a research project that tries to not only look at this problem of developing tools for performance analysis of in situ systems but also to understand how to do in situ analytics of the monitoring streams themselves. This is critical at scale, as the amount of performance data collected by the system could easily exceed the amount of data being generated by the simulation code, and we already know that there is an I/O bottleneck generated by the latter.

As such, this sort of research requires a reliable, repeatable benchmark, as there are substantial sources of variability in running at scale on modern machines due to other user's jobs. Being able to validate that the monitoring infrastructure is generating correct results, particularly given a set of inline analytics or reductions on the monitoring data, requires a robust benchmark. Further, because the performance behavior of the in situ analytics workflow depends upon the nature of the data (i.e. an algorithm whose performance depends on the number of cracks in a material won't give performance variations if the data is all just a bunch of zeroes), it is necessary that the benchmark be such that they can generate realistic (if not physics-accurate) sorts of data, with appropriate timing frequencies.

To support this sort of research, therefore, Skel offers an excellent set of features. Because it can be made to shape an I/O benchmark out of any supplied simulation code, if the work requires switching from a molecular dynamics simulation in situ analytics case to one based on a gyrokinetic fusion plasma simulation, it is a relatively simple matter of regenerating the I/O benchmark tool parameters and making small changes to the batch script that launches the various scale and parameter studies. Since the monitoring hooks can be pre-baked into the templates of the generated benchmarks, it also dramatically cuts down on the time to determine where appropriate instrumentation points are.

For instance, from previous work [1], we know that there can be some complex forms of internal interference that can arise when large parallel I/O, even that is supposedly synchronous, intersects with MPI collectives. Since many modern HPC interconnect architectures, from Infiniband to Cray Aries, allow for co-allocated usage of the network for communication and I/O, even slight overlaps in usage can cause significant jitter and delay in performance for the MPI collectives. A challenge for a system like MONA, therefore, is to see if it can detect and correctly provide information for root cause analysis of this sort of internal interference.

#### *B. A MONA Example*

One particular instance of a workflow being studied by the MONA project is derived from some simple in situ analytics being applied to the output of LAMMPS, a molecular dynamics application. For this in situ scenario, we are doing some simple diagnostic checking on the output, using a histogram function to enable an end user to get near-real-time feedback on data. From a monitoring perspective, being able to offer a guarantee on the near-real-time delivery requires being able to assess regular throughput and dynamically manage the data to keep up the rate of update, even if it means simplifying or reducing the data.

In order to make this a repeatable testing harness for the system, we require an I/O skeleton that can exhibit different types of dynamic interference effects in a realistic fashion. We utilize the fact that the Skel template generation can be tuned in different ways based on extended application models. This allows us to generate a family of different but related I/O skeletons; each member of the family stressing a different set of resources, such as large memory allocations or large MPI collective calls.

For the purposes of illustration, we show in Figure 10 an example of two different members of this LAMMPS family of I/O skeletons – one (a) that serves as a base case (no utilization of resources, just a periodic sleep() function), and another (b) that has the gap between write events filled with a large MPIAllgather() call. What we show in the figure is the variability in the latency of the adios close() call (which is where data is committed on the writer's side) between the two cases. Using the MONA framework, you also gather similar data at the ingress and egress of each of the in situ components; due to asynchronous, buffered executions, the characteristic histograms of the writer and the reader of the same data stream may vary considerably, even before you put impinging dynamic contention into consideration. As one can see from the two images, even restricted to just the write side, which is dominated by the caching behavior of the local hosts, you can see a differentiation in the distribution of latencies. Skel therefore allows one to construct increasingly refined models with different types of dynamic resource utilization to allow us to reliably test the ability of the monitoring infrastructure to measure and to diagnose the observed performance.

### VII. RELATED WORK

There is an extensive literature on and using I/O benchmarks of many sorts, as well as of tools used for performance understanding. As has been mentioned earlier, IOR is a commonly used tool [16], but it has a very specific template of I/O activity that it supports. Other projects, like FlashI/O [13] or the NAS BTIO Benchmark [31] are similarly targeted at specific I/O patterns derived from other use cases. A very nice list of such tools is curated by Rajeev Thakur at Argonne [25].

![](_page_7_Figure_0.png)

![](_page_7_Figure_1.png)

Unlike these tools, which sample the behavior of a particular code or suite of codes at one point in time and then try to codify the resulting pattern into a benchmark, the Skel approach allows for a continuous update and versioning model, where applications can respecialize the benchmark to reflect current patterns without invalidating the benchmarks generated in previous generations of code. This extends on topics developed in Ref. [32].

A second, related category of related work is in tracegeneration tools for I/O work. As we discuss above, general tracing tools like Vampir [24] or TAU [14] can be integrated with Skel to give a new set of capabilities for I/O performance understanding. There are also facility-wide tracing tools like Darshan [5] that could be used, in conjunction with Skelgenerated benchmark code, to explore how I/O performance is shaped not only by the current applications use of the I/O infrastructure, but also the impact of 3rd party applications that are causing jitter and other performance irregularities.

Finally, there is also a set of work in doing formal characterization and modeling of Scientific I/O that might bear future fruitful investigation. Techniques like ARIMA [28] could allow one to add new dynamics to both read and write I/O performance profiles in Skel. One could consider this a runtime performance analog to the data model extensions discussed in Section V.

## VIII. CONCLUSION AND FUTURE WORK

The Skel I/O benchmark generation tool allows for a much more end-user-friendly approach to generation of I/O skeletons. As has been seen in the use cases described above, this can be applied in a variety of scenarios where standard benchmarking tools might not be sufficient. The use of an I/O model provides a realistic representation of the behavior of an application of interest. Our template generation technique allows the basic benchmark to be adjusted to fit new scenarios that are arising due to new measurement techniques and advanced workflow capabilities. This flexibility will be critical in understanding and optimizing the performance of Exascale applications.

Based on our success in generating useful mini applications with Skel, we expect it to be fruitful to continue to develop this work. In particular, we will continue to refine the data generation process and examine the behavior of the synthetic data sets with a wider range of compression methods. In addition, we will incorporate feedback from the case studies explored here into the Skel standard model. Finally, a key area of improvement will be around model extensions aimed at representing and generating in situ workflows.

## ACKNOWLEDGMENTS

This material is based upon work supported by the U.S. Department of Energy, Office of Science, Office of Advanced Scientific Computing Research, Program Manager Dr. Lucy Nowell, under Award Number DE-SC0012537. Also, this research used resources of the Oak Ridge Leadership Computing Facility, which is a DOE Office of Science User Facility.

Support was also provided by the National Science Foundation under Grant Number 1265403. Any opinions, findings, and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the National Science Foundation.

## REFERENCES

- [1] H. Abbasi, J. Lofstead, F. Zheng, K. Schwan, M. Wolf, and S. Klasky. Extending I/O through high performance data services. In *2009 IEEE International Conference on Cluster Computing and Workshops*, pages 1–10, Aug 2009.
- [2] E. Bayaktar, H. V. Poor, and K. R. Sircar. Estimating the fractal dimension of the S&P 500 index using wavelet analysis. *International Journal of Theoretical and Applied Finance*, 07(05):615–643, 2004.
- [3] A. Brouste and M. Fukasawa. Local asymptotic normality property for fractional Gaussian noise under high-frequency observations. *arXiv preprint arXiv:1610.03694*, 2016.
- [4] A. Brouste, J. Istas, and S. Lambert-Lacroix. On fractional Gaussian random fields simulations. *Journal of Statistical Software, Articles*, 23(1):1–23, 2007.
- [5] P. Carns, K. Harms, W. Allcock, C. Bacon, S. Lang, R. Latham, and R. Ross. Understanding and improving computational science storage access through continuous characterization. *Trans. Storage*, 7(3):8:1– 8:26, Oct. 2011.
- [6] C. Chang, S. Ku, P. Diamond, Z. Lin, S. Parker, T. Hahm, and N. Samatova. Compressed ion temperature gradient turbulence in diverted tokamak edge a. *Physics of Plasmas*, 16(5):056108, 2009.
- [7] Cheetah, the python-powered template engine. https://pythonhosted.org/ Cheetah/.
- [8] S. Di and F. Cappello. Fast error-bounded lossy hpc data compression with sz. In *Parallel and Distributed Processing Symposium, 2016 IEEE International*, pages 730–739. IEEE, 2016.
- [9] A. Dieker and M. Mandjes. On spectral simulation of fractional Brownian motion. *Probability in the Engineering and Informational Sciences*, 17(3):417–434, 2003.
- [10] C. Docan, M. Parashar, and S. Klasky. Dataspaces: an interaction and coordination framework for coupled simulation workflows. *Cluster Computing*, 15(2):163–181, 2012.
- [11] Exascale computing project. https://exascaleproject.org/.
- [12] W. Feller. The asymptotic distribution of the range of sums of independent random variables. *Ann. Math. Statist.*, 22(3):427–432, 09 1951.

- [13] Flash I/O benchmark, derived from the FLASH HPC code. http://www. ucolick.org/∼zingale/flash benchmark io/.
- [14] K. Huck, S. Shende, A. Malony, H. Kaiser, A. Porterfield, R. Fowler, and R. Brightwell. An early prototype of an autonomic performance environment for exascale. In *Proceedings of the 3rd International Workshop on Runtime and Operating Systems for Supercomputers*, page 8. ACM, 2013.
- [15] H. E. Hurst. Long-term storage capacity of reservoirs. *Transactions of the American Society of Civil Engineers*, 116:770–799, 1951.
- [16] IOR benchmark suite. https://github.com/chaos/ior.
- [17] M. Kutare, G. Eisenhauer, C. Wang, K. Schwan, V. Talwar, and M. Wolf. Monalytics: online monitoring and analytics for managing large scale data centers. In *Proceedings of the 7th international conference on Autonomic computing*, pages 141–150. ACM, 2010.
- [18] P. Lindstrom. Fixed-rate compressed floating-point arrays. *IEEE transactions on visualization and computer graphics*, 20(12):2674–2683, 2014.
- [19] Q. Liu, J. Logan, Y. Tian, H. Abbasi, N. Podhorszki, J. Y. Choi, S. Klasky, R. Tchoua, J. Lofstead, R. Oldfield, et al. Hello ADIOS: the challenges and lessons of developing leadership class I/O frameworks. *Concurrency and Computation: Practice and Experience*, 26(7):1453– 1473, 2014.
- [20] J. Logan, S. Klasky, H. Abbasi, Q. Liu, G. Ostrouchov, M. Parashar, N. Podhorszki, Y. Tian, and M. Wolf. Understanding I/O performance using I/O skeletal applications. In *European Conference on Parallel Processing*, pages 77–88. Springer Berlin Heidelberg, 2012.
- [21] J. Logan, S. Klasky, J. Lofstead, H. Abbasi, S. Ethier, R. Grout, S. H. Ku, Q. Liu, X. Ma, M. Parashar, N. Podhorszki, K. Schwan, and M. Wolf. Skel: Generative software for producing skeletal I/O applications. In *e-Science Workshops (eScienceW), 2011 IEEE Seventh International Conference on*, pages 191–198, Dec 2011.
- [22] B. B. Mandelbrot and J. W. V. Ness. Fractional Brownian motions, fractional noises and applications. *SIAM Review*, 10(4):422–437, 1968.
- [23] A. I. McLeod, H. Yu, and Z. Krougly. Algorithms for linear time series analysis: With R package. *Journal of Statistical Software, Articles*, 23(5):1–26, 2007.

- [24] W. E. Nagel, A. Arnold, M. Weber, H.-C. Hoppe, and K. Solchenbach. VAMPIR: Visualization and analysis of MPI resources. 1996.
- [25] Parallel I/O benchmarks, applications, traces. curated by Rajeev Thakur. https://www.mcs.anl.gov/∼thakur/pio-benchmarks.html.
- [26] R. Rabenseifner and A. E. Koniges. *Effective File-I/O Bandwidth Benchmark*, pages 1273–1283. Springer Berlin Heidelberg, Berlin, Heidelberg, 2000.
- [27] H. Shan and J. Shalf. Using IOR to analyze the I/O performance for HPC platforms. In *In: Cray User Group Conference (CUG'07)*, 2007.
- [28] N. Tran and D. A. Reed. Automatic ARIMA time series modeling for adaptive I/O prefetching. *IEEE Transactions on Parallel and Distributed Systems*, 15(4):362–377, 2004.
- [29] L. Wan, M. Wolf, F. Wang, J. Choi, G. Ostrouchov, and S. Klasky. Comprehensive measurement and analysis of the user-perceived I/O performance in a production leadership-class storage system. In *Proceedings of the 37th IEEE International Conference on Distributed Computing Systems (ICDCS)*, 2017.
- [30] P. M. Widener, K. B. Ferreira, S. Levy, P. G. Bridges, D. Arnold, and R. Brightwell. *Asking the Right Questions: Benchmarking Fault-Tolerant Extreme-Scale Systems*, pages 717–726. Springer Berlin Heidelberg, Berlin, Heidelberg, 2014.
- [31] P. Wong and R. F. van der Wijngaart. NAS Parallel Benchmarks I/O Version 2.4. Technical Report NAS Technical Report NAS-03-002, NASA Ames Research Center, Moffett Field, CA, 2003.
- [32] Z. Zhang and D. S. Katz. Using application skeletons to improve escience infrastructure. In *Proceedings of the 2014 IEEE 10th International Conference on e-Science - Volume 01*, E-SCIENCE '14, pages 111–118, Washington, DC, USA, 2014. IEEE Computer Society.
- [33] F. Zheng, H. Abbasi, C. Docan, J. Lofstead, Q. Liu, S. Klasky, M. Parashar, N. Podhorszki, K. Schwan, and M. Wolf. Predata– preparatory data analytics on peta-scale machines. In *Parallel & Distributed Processing (IPDPS), 2010 IEEE International Symposium* on, pages 1–12. IEEE, 2010.

571

