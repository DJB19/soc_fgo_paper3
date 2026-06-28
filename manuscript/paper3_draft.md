# Evaluation of FGO-Based Battery SOC Estimation Under Aging Conditions Using Public Experimental Datasets

## Abstract

Accurate state-of-charge (SOC) estimation remains challenging for lithium-ion batteries under aging conditions because capacity degradation changes the relationship between current integration and the actual available charge. This study evaluates factor graph optimization (FGO)-based SOC estimation using public NASA lithium-ion battery aging datasets. Unlike simulation-only evaluations, experimentally measured discharge data are used, and reference SOC trajectories are reconstructed from measured discharge capacity. Battery B0005 is first used as a representative case to establish the preprocessing, baseline evaluation, and FGO-based estimation workflow. The method is then extended to B0006, B0007, and B0018 for cross-cell validation.

The results show that nominal-capacity Coulomb Counting produces increasing SOC errors as battery capacity degrades. A fixed-capacity FGO formulation with a voltage factor provides only limited improvement because the capacity remains fixed to the initial value. To address this limitation, a physically constrained capacity-aware FGO formulation is introduced. In this formulation, the SOC trajectory is generated from cumulative discharged capacity and an estimated effective capacity, which enforces a monotonic SOC decrease during discharge. Across the tested NASA cells, the proposed method consistently reduces the SOC RMSE in middle and late aging stages compared with nominal-capacity Coulomb Counting. These results demonstrate that the main advantage of FGO for aged battery SOC estimation lies in its ability to incorporate physical constraints and aging-related parameters into a unified optimization framework.

**Keywords:** lithium-ion battery; state of charge; factor graph optimization; capacity degradation; battery aging; Coulomb Counting; NASA battery dataset

## 1. Introduction

Lithium-ion batteries are widely used in electric vehicles, renewable energy storage systems, portable electronics, and other electrified systems. The performance, safety, and lifetime of these systems depend strongly on the reliability of the battery management system. Among the core functions of a battery management system, state-of-charge estimation is one of the most important tasks because it provides information about the remaining usable capacity of the battery. Accurate SOC estimation is necessary for driving range prediction, charge and discharge control, energy management, and safety protection.

However, SOC cannot be measured directly by a physical sensor. It must be estimated from measurable signals such as current, terminal voltage, and temperature. This estimation problem is challenging because lithium-ion batteries exhibit nonlinear electrochemical behavior, aging-related capacity degradation, temperature dependency, and measurement noise. In addition, the same estimation algorithm may perform differently across different batteries, different cycles, and different aging stages. Therefore, evaluating SOC estimation methods using real experimental battery data is an important step before practical application.

Traditional SOC estimation methods include Coulomb Counting, model-based filtering methods, and data-driven methods. Coulomb Counting estimates SOC by integrating the battery current over time. It is simple and easy to implement, but it is sensitive to initial SOC error, current sensor bias, and capacity uncertainty. Kalman-filter-based methods, such as the Kalman Filter, Extended Kalman Filter, and Unscented Kalman Filter, combine battery models and sensor measurements in a recursive estimation framework. These methods have been widely used in battery management systems because of their computational efficiency. However, their performance depends on the accuracy of the battery model, noise covariance settings, and linearization assumptions.

Factor graph optimization provides another framework for battery state estimation. In a factor graph, the unknown battery states are represented as variable nodes, and the relationships derived from system dynamics and sensor measurements are represented as factor nodes. The estimation problem is formulated as an optimization problem that minimizes the total residual error over the graph. Compared with purely recursive filtering, FGO can naturally incorporate multiple constraints and perform smoothing over a sequence of states. This characteristic makes it potentially useful for battery SOC estimation, especially under noisy measurement conditions.

Our previous study evaluated the robustness of FGO-based SOC estimation using a self-developed C++ battery model under controlled noise conditions. In that study, the noise level and model conditions could be adjusted systematically, which was useful for understanding the basic robustness characteristics of FGO. However, validation using real experimental battery data was still limited. Real battery datasets include measurement noise, capacity degradation, cycle-to-cycle variation, and operating condition changes that cannot be fully represented by a simplified simulation model. Therefore, a more systematic evaluation using public experimental battery datasets is needed.

The present study addresses this limitation by evaluating FGO-based SOC estimation under aging conditions using public lithium-ion battery datasets. The main focus is on discharge cycles because they provide measurable current, voltage, and capacity information that can be used to reconstruct reference SOC. Multiple batteries and multiple aging stages are selected to analyze whether FGO can maintain stable SOC estimation performance as the battery degrades. The proposed evaluation framework compares FGO with conventional baseline methods using quantitative error metrics.

This work is also relevant to future battery digital twin applications. A battery digital twin requires a reliable state estimation module to synchronize the virtual battery model with measured battery data. Although this paper does not construct a complete online battery digital twin system, it evaluates an FGO-based state estimation module that may serve as a core component of future digital twin-based battery monitoring systems.

The main contributions of this paper are summarized as follows:

1. A public-data-based SOC estimation evaluation workflow is constructed using NASA lithium-ion battery aging datasets. Discharge cycles are extracted from B0005, B0006, B0007, and B0018, and reference SOC trajectories are reconstructed from measured discharge capacity.

2. The influence of capacity degradation on conventional nominal-capacity Coulomb Counting is quantitatively analyzed across multiple aging stages. The results show that using a fixed initial capacity leads to increasing SOC overestimation as the battery ages.

3. A physically constrained capacity-aware FGO formulation is proposed for aged battery SOC estimation. In this formulation, the SOC trajectory is generated from cumulative discharged capacity and an estimated effective capacity, which enforces a monotonic SOC decrease during discharge.

4. Cross-cell validation is conducted using four NASA battery cells. The proposed method consistently reduces SOC estimation errors in middle and late aging stages compared with nominal-capacity Coulomb Counting, demonstrating the potential of FGO for aging-aware SOC estimation.

## 2. Public Battery Dataset and Data Preprocessing

### 2.1 Public Battery Aging Dataset

This study uses public lithium-ion battery aging data to evaluate the applicability of factor graph optimization for SOC estimation under real experimental aging conditions. Different from simulation-generated data, public experimental battery datasets contain practical non-ideal characteristics such as measurement noise, capacity degradation, cycle-to-cycle variation, and inconsistent discharge duration. These characteristics are important for evaluating whether a state estimation algorithm can be applied beyond controlled simulation environments.

The primary dataset used in this study is the NASA lithium-ion battery aging dataset. The dataset contains repeated charge, discharge, and impedance measurement profiles for several lithium-ion cells. In this work, the discharge profiles are selected because they provide time-series measurements of current, terminal voltage, temperature, and discharge capacity, which are suitable for SOC reconstruction and estimation evaluation.

Four NASA battery cells are used in this study: B0005, B0006, B0007, and B0018. Battery B0005 is first used as the main representative case to establish the preprocessing workflow, baseline comparison, and FGO-based SOC estimation procedure. The same workflow is then extended to B0006, B0007, and B0018 for cross-cell validation. This design allows the proposed method to be evaluated not only on a single cell, but also across different degradation trajectories.

The extracted discharge cycles include 168 cycles for B0005, 168 cycles for B0006, 168 cycles for B0007, and 132 cycles for B0018. For each battery, representative early-, middle-, and late-aging discharge cycles are selected for detailed SOC estimation analysis. The early stage corresponds to the first discharge cycle, the late stage corresponds to the final discharge cycle, and the middle stage is selected near the midpoint of the available discharge-cycle sequence.

The converted data format includes battery ID, raw cycle index, discharge cycle ID, time, measured terminal voltage, measured current, measured temperature, measured discharge capacity, cumulative discharged capacity, and reconstructed reference SOC. This unified format allows the same estimation program to be applied consistently to multiple batteries and aging stages.

### 2.2 Discharge Cycle Extraction

The original NASA data file contains different types of operation profiles, including charge, discharge, and impedance measurement. Since this paper focuses on SOC estimation during battery discharge, only discharge cycles are extracted. For each discharge cycle, the following signals are obtained:

\[
t_k,\quad I_k,\quad V_k,\quad T_k,\quad Q_{\mathrm{cycle}}
\]

where \(t_k\) is the time at sample \(k\), \(I_k\) is the measured current, \(V_k\) is the measured terminal voltage, \(T_k\) is the measured temperature, and \(Q_{\mathrm{cycle}}\) is the measured discharge capacity of the corresponding cycle.

The discharge cycles are indexed sequentially after extraction. For battery B0005, 168 discharge cycles are obtained. The early, middle, and late aging stages are represented by selected discharge cycles from the beginning, middle, and end of the extracted cycle sequence. In the initial experiment, cycle 1, cycle 84, and cycle 168 are used as representative cycles for early-stage, middle-stage, and late-stage battery aging, respectively.

This selection strategy allows the influence of battery aging on SOC estimation performance to be analyzed. As the battery ages, the available discharge capacity decreases, and the voltage response may also change. Therefore, comparing estimation performance across different aging stages is useful for evaluating the robustness and practical applicability of the proposed FGO-based SOC estimation framework.

### 2.3 Reference SOC Reconstruction

Since SOC is not directly measured by a physical sensor in the public dataset, a reference SOC trajectory is reconstructed from the discharge capacity of each cycle. At the beginning of each discharge cycle, SOC is assumed to be 1.0, corresponding to a fully charged state. During discharge, the accumulated discharged capacity is calculated by integrating the absolute value of the measured current over time.

The accumulated discharged capacity at sample \(k\) is calculated as:

\[
Q_{\mathrm{dis}}(k)=\sum_{i=1}^{k} |I_i|\Delta t_i
\]

where \(I_i\) is the measured current and \(\Delta t_i\) is the sampling interval between two adjacent measurements, expressed in hours. The reconstructed reference SOC is then defined as:

\[
SOC_{\mathrm{ref}}(k)=1-\frac{Q_{\mathrm{dis}}(k)}{Q_{\mathrm{cycle}}}
\]

where \(Q_{\mathrm{cycle}}\) is the measured discharge capacity of the corresponding cycle.

The reconstructed SOC is clipped to the interval \([0,1]\) to avoid numerical values outside the physically meaningful range caused by measurement noise or numerical integration error. It should be noted that this reference SOC is not a directly measured internal electrochemical state. Instead, it is a capacity-based reference trajectory reconstructed from experimental discharge data. This definition is used as the evaluation reference for comparing different SOC estimation methods.

### 2.4 Capacity Degradation Representation

Battery aging is represented by the degradation of measured discharge capacity over repeated cycles. For each discharge cycle, the corresponding measured capacity is extracted and used to construct a capacity degradation curve. This curve provides a direct representation of the aging process of each selected battery cell.

In this study, capacity degradation is analyzed for four NASA battery cells: B0005, B0006, B0007, and B0018. The extracted discharge-cycle data show that all four cells experience capacity fade, but the degradation patterns are different among cells. B0005 contains 168 discharge cycles, with the measured capacity decreasing from 1.8565 Ah in the first cycle to 1.3251 Ah in the final cycle. B0006 also contains 168 discharge cycles and shows stronger degradation, with the capacity decreasing from 2.0353 Ah to 1.1857 Ah. B0007 contains 168 discharge cycles, with capacity decreasing from 1.8911 Ah to 1.4325 Ah. B0018 contains 132 discharge cycles, with capacity decreasing from 1.8550 Ah to 1.3411 Ah.

This capacity degradation is important for SOC estimation because the available capacity appears directly in current-integration-based state transition models. If the capacity value is assumed to be constant and is not updated with aging, SOC estimation error may accumulate. Therefore, the capacity degradation curves are used not only to describe the aging characteristics of the selected cells, but also to motivate the capacity-aware FGO formulation developed in this study.

### 2.5 Preprocessing Workflow

The complete preprocessing workflow is summarized as follows:

1. Load the original NASA MATLAB battery data file.
2. Extract only discharge cycles from the complete operation profiles.
3. Obtain current, voltage, temperature, time, and measured capacity for each discharge cycle.
4. Reconstruct reference SOC using the accumulated discharged capacity.
5. Save all extracted and reconstructed variables into a unified CSV file.
6. Generate cycle-level summary information, including cycle length, measured capacity, voltage range, and SOC range.
7. Select representative early, middle, and late aging cycles for detailed analysis.

This preprocessing procedure transforms the original public battery dataset into a structured format suitable for FGO-based SOC estimation experiments. It also provides the basis for aging-stage comparison and capacity-error relationship analysis in the following sections.


## 3. SOC Estimation Methods

This section describes the SOC estimation methods and optimization formulations used in this study. Coulomb Counting is first introduced as a basic current-integration baseline because it directly reflects the influence of capacity uncertainty on SOC estimation. A fixed-capacity FGO formulation is then considered to evaluate whether adding a voltage factor can improve SOC estimation when the capacity remains fixed. Finally, a physically constrained capacity-aware FGO formulation is introduced as the main proposed method. In this formulation, the effective capacity is estimated and the SOC trajectory is generated from cumulative discharged capacity, which enforces physically consistent monotonic SOC behavior during discharge.

Although Kalman-filter-based methods are widely used for battery SOC estimation, the quantitative comparison in this study focuses on Coulomb Counting and FGO-based formulations. This choice is made because the main objective is to isolate the influence of capacity degradation and to evaluate whether FGO can incorporate aging-related capacity parameters into the estimation framework.

### 3.1 Coulomb Counting

Coulomb Counting estimates SOC by integrating the measured battery current over time. In discrete time, the SOC update equation can be written as:

\[
SOC_k = SOC_{k-1} - \frac{\eta I_k \Delta t_k}{Q}
\]

where \(SOC_k\) is the estimated SOC at sample \(k\), \(\eta\) is the coulombic efficiency, \(I_k\) is the measured current, \(\Delta t_k\) is the sampling interval, and \(Q\) is the available battery capacity.

Coulomb Counting is simple and computationally efficient. However, it is sensitive to the initial SOC value, current sensor error, and capacity uncertainty. Under battery aging conditions, the available capacity decreases gradually. If the capacity value is not updated properly, the SOC estimation error may accumulate over time. Therefore, Coulomb Counting is used in this paper as a basic reference method for evaluating the benefit of model-based and optimization-based methods.

In this study, the initial SOC at the beginning of each discharge cycle is set to 1.0. The measured discharge capacity of each cycle is used as the capacity value for reconstructing the reference SOC. For baseline estimation, both cycle-specific capacity and nominal-capacity settings can be considered to analyze the influence of capacity uncertainty.

### 3.2 Model-Based Recursive Estimation Background

Kalman-filter-based methods are widely used for battery SOC estimation because they can recursively combine a battery state transition model with voltage measurements. In a simplified SOC estimation problem, the state transition model can be derived from the current integration equation:

\[
SOC_k = SOC_{k-1} - \frac{\eta I_k \Delta t_k}{Q} + w_k
\]

where \(w_k\) represents process noise. The voltage measurement equation can be expressed as:

\[
V_k = h(SOC_k, I_k, \theta) + v_k
\]

where \(V_k\) is the measured terminal voltage, \(h(\cdot)\) is the voltage prediction function, \(\theta\) represents battery model parameters, and \(v_k\) represents measurement noise.

For linear systems, the standard Kalman Filter can be applied. For nonlinear battery voltage models, Extended Kalman Filter or Unscented Kalman Filter formulations are usually required. These recursive estimators are computationally efficient, but their performance depends on the accuracy of the battery model, the noise covariance settings, and the validity of linearization or approximation assumptions.

In this study, Kalman-filter-based estimation is discussed as a conventional model-based background. The quantitative experiments focus on Coulomb Counting and FGO-based formulations because the main objective is to investigate how capacity degradation affects current-integration-based SOC estimation and how FGO can incorporate capacity-related aging parameters into the optimization problem.

### 3.3 Factor Graph Optimization

Factor graph optimization formulates SOC estimation as an optimization problem over a sequence of battery states. In the factor graph representation, each SOC state is represented as a variable node, and each model or measurement constraint is represented as a factor node. The optimal SOC trajectory is obtained by minimizing the total residual error associated with all factors.

For SOC estimation, the dynamic factor is derived from the current integration relationship between consecutive SOC states:

\[
r_{d,k} = SOC_k - SOC_{k-1} + \frac{\eta I_k \Delta t_k}{Q}
\]

where \(r_{d,k}\) is the dynamic residual. The voltage measurement factor is defined as:

\[
r_{v,k} = V_k - h(SOC_k, I_k, \theta)
\]

where \(r_{v,k}\) is the voltage measurement residual. A prior factor is also added to constrain the initial SOC value at the beginning of each discharge cycle:

\[
r_p = SOC_0 - \hat{SOC}_0
\]

where \(\hat{SOC}_0\) is the assumed initial SOC.

The FGO objective function can be written as:

\[
\min_{\{SOC_k\}} \sum_k \|r_{d,k}\|^2_{\Sigma_d^{-1}} + \sum_k \|r_{v,k}\|^2_{\Sigma_v^{-1}} + \|r_p\|^2_{\Sigma_p^{-1}}
\]

where \(\Sigma_d\), \(\Sigma_v\), and \(\Sigma_p\) represent the covariance or weighting terms of the dynamic, voltage measurement, and prior factors, respectively.

Compared with Coulomb Counting, FGO can use both current-based dynamic constraints and voltage-based measurement constraints. Compared with recursive Kalman-filter-based estimation, FGO can optimize multiple states jointly and perform smoothing over a state sequence. This makes FGO potentially more robust under real experimental measurement noise and cycle-to-cycle variation.

### 3.4 Application to Public Battery Aging Data

When applying FGO to public battery aging data, several practical issues must be considered. First, the available capacity changes as the battery ages. Therefore, the capacity value used in the dynamic factor should be selected carefully. Second, the voltage-SOC relationship may vary across cycles because of aging, temperature variation, and internal resistance change. Third, the reference SOC is reconstructed from discharge capacity and is not directly measured.

In this study, FGO is evaluated on selected discharge cycles from different aging stages. The same preprocessing procedure and evaluation metrics are applied to all methods. This allows the estimation performance of FGO to be compared with baseline methods under consistent experimental conditions.


## 4. Experimental Design and Evaluation Metrics

### 4.1 Experimental Objective

The objective of the experiments is to evaluate the applicability of FGO-based SOC estimation under real battery aging conditions. Unlike controlled simulation experiments, the public battery aging dataset contains real measurement noise, capacity degradation, cycle-to-cycle variation, and changes in voltage response. These characteristics make it suitable for investigating whether FGO can maintain stable SOC estimation performance when applied to experimental battery data.

The experiments are designed to answer the following research questions:

1. Can FGO estimate SOC accurately using public experimental lithium-ion battery discharge data?
2. How does SOC estimation performance change from early aging stages to late aging stages?
3. Compared with conventional baseline methods, does FGO provide more stable estimation under real measurement conditions?
4. How is SOC estimation error related to capacity degradation across discharge cycles?

### 4.2 Selected Battery and Aging Stages

Battery B0005 is used as the first evaluation object in this study. From the original NASA MATLAB data file, 168 discharge cycles are extracted and converted into a unified CSV format. Each discharge cycle contains measured current, terminal voltage, temperature, time, measured discharge capacity, and reconstructed reference SOC.

To analyze the influence of battery aging, three representative discharge cycles are selected:

\[
\text{early stage: cycle 1}
\]

\[
\text{middle stage: cycle 84}
\]

\[
\text{late stage: cycle 168}
\]

These cycles represent the beginning, middle, and end of the extracted aging sequence. The early-stage cycle corresponds to a relatively fresh battery condition, while the late-stage cycle corresponds to a more degraded battery condition. The middle-stage cycle provides an intermediate aging condition.

In addition to these three representative cycles, all 168 discharge cycles are used to construct the capacity degradation curve. This curve is used to analyze the relationship between battery aging and SOC estimation performance.

### 4.3 Experimental Cases

The experimental cases are organized as follows:

**Case 1: Early-stage SOC estimation.**  
SOC estimation is performed on discharge cycle 1 of battery B0005. This case evaluates the performance of different methods under a relatively fresh battery condition.

**Case 2: Middle-stage SOC estimation.**  
SOC estimation is performed on discharge cycle 84. This case evaluates the performance of different methods under an intermediate aging condition.

**Case 3: Late-stage SOC estimation.**  
SOC estimation is performed on discharge cycle 168. This case evaluates the performance of different methods under a more degraded battery condition.

**Case 4: Capacity degradation analysis.**  
The measured discharge capacity of all 168 discharge cycles is extracted and plotted against cycle index. This case provides a direct representation of the aging process of battery B0005.

**Case 5: Capacity-error relationship analysis.**  
After SOC estimation is performed across multiple cycles, the relationship between measured discharge capacity and SOC estimation error will be analyzed. This case is used to investigate whether estimation performance deteriorates as battery capacity decreases.

### 4.4 Compared Methods

The quantitative comparison focuses on three SOC estimation methods:

1. Nominal-capacity Coulomb Counting,
2. Fixed-capacity FGO,
3. Physically constrained capacity-aware FGO.

Nominal-capacity Coulomb Counting uses the initial discharge capacity as a fixed nominal capacity for all aging stages. This method represents a simple baseline for evaluating the influence of capacity degradation.

Fixed-capacity FGO uses the same nominal capacity but introduces a voltage-related factor into the optimization framework. This method is used to examine whether adding a voltage factor alone can improve SOC estimation under aging conditions.

The physically constrained capacity-aware FGO is the main proposed method. It estimates an effective capacity and generates the SOC trajectory from cumulative discharged capacity. This formulation enforces a monotonic SOC decrease during discharge and explicitly accounts for capacity degradation.

### 4.5 Evaluation Metrics

The SOC estimation performance is evaluated using several quantitative metrics. Let \(SOC_{\mathrm{est},k}\) denote the estimated SOC at sample \(k\), and let \(SOC_{\mathrm{ref},k}\) denote the reconstructed reference SOC. The estimation error is defined as:

\[
e_k = SOC_{\mathrm{est},k} - SOC_{\mathrm{ref},k}
\]

The root mean square error is calculated as:

\[
RMSE = \sqrt{\frac{1}{N}\sum_{k=1}^{N} e_k^2}
\]

where \(N\) is the number of samples in the selected discharge cycle.

The mean absolute error is calculated as:

\[
MAE = \frac{1}{N}\sum_{k=1}^{N} |e_k|
\]

The maximum absolute error is calculated as:

\[
MaxError = \max_k |e_k|
\]

The standard deviation of the estimation error is calculated as:

\[
STD = \sqrt{\frac{1}{N}\sum_{k=1}^{N}(e_k-\bar{e})^2}
\]

where \(\bar{e}\) is the mean estimation error.

RMSE and MAE are used to evaluate overall estimation accuracy. Maximum absolute error is used to evaluate worst-case deviation. Error standard deviation is used to evaluate the stability of the estimation error. Together, these metrics provide a comprehensive evaluation of SOC estimation performance under different aging conditions.

### 4.6 Figure and Table Design

The experimental results will be presented using both figures and tables. The planned figures include:

1. Voltage, current, and reconstructed SOC curves for representative discharge cycles.
2. Capacity degradation curve of battery B0005 across 168 discharge cycles.
3. SOC estimation comparison curves for early, middle, and late aging stages.
4. SOC estimation error curves for different methods.
5. RMSE variation across selected cycles or aging stages.
6. Relationship between measured capacity and SOC estimation error.

The planned tables include:

1. Summary of selected discharge cycles.
2. Quantitative SOC estimation errors for early-stage, middle-stage, and late-stage cycles.
3. Comparison of RMSE, MAE, maximum error, and error standard deviation for all methods.
4. Capacity and estimation error summary across aging stages.

This experimental design allows both visual and quantitative comparison of different SOC estimation methods under real battery aging conditions.


## 5. Results and Discussion

### 5.1 Dataset Characteristics and Capacity Degradation

The extracted B0005 dataset contains 168 discharge cycles. Each discharge cycle includes measured terminal voltage, current, temperature, time, and measured discharge capacity. Based on the extracted discharge profiles, reference SOC trajectories were reconstructed using the measured capacity of each cycle.

The capacity degradation curve shows a clear decrease in measured discharge capacity over repeated discharge cycles. The measured capacity of the first discharge cycle is 1.8565 Ah, which is used as the initial reference capacity in this study. For the representative aging-stage cycles, the measured capacities are 1.8565 Ah for cycle 1, 1.5489 Ah for cycle 84, and 1.3251 Ah for cycle 168. The corresponding capacity ratios relative to cycle 1 are 1.0000, 0.8343, and 0.7138, respectively.

These results confirm that the selected cycles represent different aging stages of battery B0005. Cycle 1 represents the early stage, cycle 84 represents the middle stage, and cycle 168 represents the late stage. The significant decrease in measured capacity indicates that battery aging should not be ignored in SOC estimation. Since the available capacity appears directly in current-integration-based SOC estimation models, capacity degradation can introduce substantial estimation error if the capacity value is not updated.

The representative voltage, current, and reconstructed SOC curves also show that the discharge duration and voltage response vary across aging stages. These variations reflect real experimental characteristics that are not fully captured by simplified simulation models. Therefore, the public battery aging dataset provides a meaningful basis for evaluating SOC estimation methods under realistic aging conditions.

### 5.2 Coulomb Counting Baseline and Capacity Degradation Effect

Two Coulomb Counting settings were evaluated. The first setting uses the measured capacity of each discharge cycle. The second setting fixes the capacity to the measured capacity of cycle 1 and uses it as the nominal capacity for all selected aging-stage cycles.

When the measured capacity of each individual discharge cycle is used, the Coulomb Counting result is almost identical to the reconstructed reference SOC. The RMSE values for cycle 1, cycle 84, and cycle 168 are on the order of \(10^{-17}\). This result is expected because both the reconstructed reference SOC and the cycle-specific Coulomb Counting estimator are based on the same current integration and the same measured cycle capacity. Therefore, this result should not be interpreted as a practical advantage of Coulomb Counting. Instead, it verifies the consistency of the data preprocessing, reference SOC reconstruction, and metric calculation procedures.

In contrast, when the capacity of cycle 1 is fixed as the nominal capacity, the SOC estimation error increases significantly as the battery ages. For cycle 1, the RMSE remains nearly zero because the nominal capacity is equal to the measured capacity of that cycle. For cycle 84, where the capacity ratio decreases to approximately 0.8343, the RMSE increases to approximately 0.1041. For cycle 168, where the capacity ratio further decreases to approximately 0.7138, the RMSE increases to approximately 0.1881.

This result demonstrates that capacity degradation has a direct impact on current-integration-based SOC estimation. If a battery management system continues to use the initial nominal capacity while the actual available capacity decreases, SOC estimation error will accumulate and become increasingly significant in later aging stages. Therefore, aging-aware capacity information or additional measurement constraints are necessary for reliable SOC estimation over the battery lifetime.

The nominal-capacity Coulomb Counting result also provides a useful motivation for evaluating model-based and optimization-based methods. Since factor graph optimization can incorporate both dynamic constraints and voltage measurement constraints, it may provide a more flexible framework for SOC estimation under aging conditions. The following sections will further evaluate whether FGO can improve SOC estimation stability compared with conventional baseline methods.


### 5.3 FGO-Based SOC Estimation Results

After evaluating the Coulomb Counting baselines, FGO-based SOC estimation was further investigated using the selected aging stages of battery B0005. Three representative discharge cycles were used: cycle 1 for the early stage, cycle 84 for the middle aging stage, and cycle 168 for the late aging stage. The objective was to examine whether the FGO framework could reduce the SOC estimation error caused by capacity degradation.

A fixed-capacity FGO was first implemented. In this case, the capacity was fixed to the initial capacity of cycle 1, while a voltage factor was added using an empirical voltage-SOC relationship fitted from the early-stage discharge data. This method provided only limited improvement over nominal-capacity Coulomb Counting. For cycle 84, the RMSE decreased from 0.1041 to 0.0889. For cycle 168, the RMSE decreased only slightly from 0.1881 to 0.1837. These results indicate that simply adding a voltage factor is insufficient when the capacity is still assumed to be constant. The effectiveness of FGO under aging conditions depends strongly on whether the model can account for capacity degradation.

To address this limitation, a physically constrained capacity-aware FGO formulation was introduced. Instead of treating all SOC states as independent optimization variables, the SOC trajectory was parameterized using the cumulative discharged capacity and an estimated effective capacity. The SOC at time step \(k\) was expressed as

\[
SOC_k = 1 - \frac{Q_{\mathrm{dis}}(k)}{Q_{\mathrm{eff}}},
\]

where \(Q_{\mathrm{dis}}(k)\) is the cumulative discharged capacity and \(Q_{\mathrm{eff}}\) is the effective capacity estimated by the optimization. This formulation guarantees a physically consistent monotonic SOC decrease during discharge and avoids non-physical SOC recovery in the late-discharge region.

The physically constrained capacity-aware FGO significantly improved the SOC estimation accuracy. In cycle 84, the RMSE was reduced from 0.1041 for nominal-capacity Coulomb Counting to 0.0089. In cycle 168, the RMSE was reduced from 0.1881 to 0.0196. These results correspond to RMSE reductions of approximately 91.5% and 89.5%, respectively. The estimated effective capacities were also close to the reconstructed cycle capacities. For cycle 84, the true cycle capacity was 1.5489 Ah and the estimated capacity was 1.5717 Ah. For cycle 168, the true cycle capacity was 1.3251 Ah and the estimated capacity was 1.3669 Ah.

Figure 3 compares the SOC trajectories for the late-stage cycle 168. The nominal-capacity Coulomb Counting method overestimates SOC because it uses the initial capacity and does not account for aging-induced capacity loss. In contrast, the physically constrained capacity-aware FGO produces a monotonic SOC trajectory that closely follows the reconstructed reference SOC. A small residual offset remains near the end of discharge, mainly because the estimated effective capacity is slightly higher than the reconstructed cycle capacity.

Figure 4 summarizes the RMSE comparison among nominal-capacity Coulomb Counting, fixed-capacity FGO, and physically constrained capacity-aware FGO. The results show that the main advantage of FGO in aged battery SOC estimation is not merely the inclusion of a voltage factor, but the ability to incorporate capacity-related parameters into a unified optimization framework.


### 5.4 Quantitative Comparison of SOC Estimation Methods

Table 2 summarizes the SOC estimation performance of the three methods for B0005 under different aging stages. The nominal-capacity Coulomb Counting method shows increasing error as the battery ages because it uses the initial capacity throughout all cycles. The fixed-capacity FGO provides only limited improvement, indicating that the voltage factor alone is insufficient when the capacity remains fixed. In contrast, the physically constrained capacity-aware FGO significantly reduces the SOC estimation error in both the middle and late aging stages by estimating the effective capacity and enforcing a monotonic discharge trajectory.

Table 2. SOC estimation performance comparison for B0005 under different aging stages.

| Stage | Cycle | Method | True Capacity (Ah) | Estimated Capacity (Ah) | RMSE | MAE | Max Error |
|---|---:|---|---:|---:|---:|---:|---:|
| early | 1 | Nominal-Capacity CC | 1.8565 | - | 0.0000 | 0.0000 | 0.0000 |
| early | 1 | Fixed-Capacity FGO | 1.8565 | - | 0.0169 | 0.0120 | 0.0671 |
| early | 1 | Physical CA-FGO | 1.8565 | 1.8288 | 0.0081 | 0.0066 | 0.0149 |
| middle | 84 | Nominal-Capacity CC | 1.5489 | - | 0.1041 | 0.0904 | 0.1654 |
| middle | 84 | Fixed-Capacity FGO | 1.5489 | - | 0.0889 | 0.0605 | 0.3685 |
| middle | 84 | Physical CA-FGO | 1.5489 | 1.5717 | 0.0089 | 0.0078 | 0.0145 |
| late | 168 | Nominal-Capacity CC | 1.3251 | - | 0.1881 | 0.1640 | 0.2857 |
| late | 168 | Fixed-Capacity FGO | 1.3251 | - | 0.1837 | 0.1395 | 0.5453 |
| late | 168 | Physical CA-FGO | 1.3251 | 1.3669 | 0.0196 | 0.0172 | 0.0305 |
### 5.5 Discussion

The results obtained from B0005 show that capacity degradation has a significant influence on SOC estimation when the capacity is assumed to be constant. The nominal-capacity Coulomb Counting method uses the initial capacity of cycle 1 for all aging stages. As a result, the method increasingly overestimates SOC as the battery ages. This behavior is clearly observed in the middle and late aging stages, where the RMSE increases to 0.1041 and 0.1881, respectively.

The fixed-capacity FGO method introduces a voltage factor into the estimation framework. However, because the capacity is still fixed to the initial value, the improvement is limited. For cycle 84, the RMSE is reduced from 0.1041 to 0.0889, while for cycle 168, the RMSE is only reduced from 0.1881 to 0.1837. These results indicate that a voltage factor alone cannot fully compensate for aging-induced capacity loss. This also suggests that the performance of FGO depends strongly on whether the model includes the dominant aging-related parameters.

The physically constrained capacity-aware FGO provides a more effective solution by estimating the effective capacity and generating the SOC trajectory from the cumulative discharged capacity. Since the SOC trajectory is parameterized by the estimated capacity, the discharge process is physically constrained to be monotonic. This avoids non-physical SOC recovery in the late-discharge region and produces more realistic SOC trajectories. Compared with nominal-capacity Coulomb Counting, the proposed method reduces the RMSE by approximately 91.5% in cycle 84 and 89.5% in cycle 168.

Another important observation is that the estimated effective capacities are close to the reconstructed cycle capacities. For cycle 84, the reconstructed capacity is 1.5489 Ah and the estimated capacity is 1.5717 Ah. For cycle 168, the reconstructed capacity is 1.3251 Ah and the estimated capacity is 1.3669 Ah. Although small deviations remain, the estimated capacities correctly reflect the decreasing trend caused by battery aging. This demonstrates that the proposed framework can provide not only SOC estimation but also useful information related to capacity degradation.

These results highlight the advantage of FGO as a flexible optimization framework. The benefit of FGO does not come only from adding more measurement factors, but from its ability to incorporate state variables, physical constraints, and aging-related parameters into a unified estimation problem. For aged batteries, this flexibility is important because SOC estimation and capacity degradation are strongly coupled.

It should also be noted that B0005 is used as the main representative case for detailed analysis, while B0006, B0007, and B0018 are used for cross-cell validation. This design allows the proposed method to be evaluated across multiple degradation trajectories. Nevertheless, the present study is still based on public laboratory aging datasets under controlled discharge conditions. Further validation using additional battery datasets, partial discharge profiles, and real-world driving conditions is needed to confirm the practical generality of the proposed method.


### 5.6 Cross-Cell Validation Using Multiple NASA Cells

To evaluate the generality of the proposed method, additional experiments were conducted on three more NASA lithium-ion cells: B0006, B0007, and B0018. Together with B0005, these four cells provide a cross-cell validation set with different initial capacities and degradation trajectories. For each battery, representative early-, middle-, and late-aging discharge cycles were selected. The cross-cell comparison focused on the middle and late aging stages, where the effect of capacity degradation on SOC estimation becomes more significant.

Figure 5 compares the RMSE values of nominal-capacity Coulomb Counting and physically constrained capacity-aware FGO across the four cells in the middle and late aging stages. In all cases, the proposed method substantially reduced the SOC estimation error. This confirms that the advantage of the proposed framework is not limited to a single battery case.

Table 3 summarizes the quantitative results. For B0005, the RMSE was reduced from 0.1041 to 0.0089 in the middle stage and from 0.1881 to 0.0196 in the late stage. For B0006, the RMSE was reduced from 0.1810 to 0.0332 in the middle stage and from 0.2897 to 0.0668 in the late stage. For B0007, the RMSE was reduced from 0.0888 to 0.0042 in the middle stage and from 0.1483 to 0.0134 in the late stage. For B0018, the RMSE was reduced from 0.1082 to 0.0198 in the middle stage and from 0.1756 to 0.0219 in the late stage.

The results also show that the estimated effective capacities followed the degradation trend of each battery. Although the estimation error varied among the batteries, the proposed method consistently produced monotonic SOC trajectories without non-physical SOC recovery. This indicates that the physically constrained capacity-aware FGO is robust across different cells and aging conditions.

Among the tested batteries, B0006 exhibited the largest SOC estimation error in the late stage, even after applying the proposed method. This is reasonable because B0006 experienced the strongest degradation among the four cells, with the capacity decreasing from 2.0353 Ah to 1.1857 Ah. Even in this more challenging case, however, the proposed method still provided a substantial improvement over nominal-capacity Coulomb Counting.

Table 3. Cross-cell SOC estimation performance comparison across middle and late aging stages.

| Battery | Stage | Cycle | True Capacity (Ah) | Estimated Capacity (Ah) | Nominal CC RMSE | Physical CA-FGO RMSE | RMSE Reduction (%) |
|---|---|---:|---:|---:|---:|---:|---:|
| B0005 | middle | 84 | 1.5489 | 1.5717 | 0.1041 | 0.0089 | 91.46 |
| B0005 | late | 168 | 1.3251 | 1.3669 | 0.1881 | 0.0196 | 89.55 |
| B0006 | middle | 84 | 1.4675 | 1.5504 | 0.1810 | 0.0332 | 81.65 |
| B0006 | late | 168 | 1.1857 | 1.3200 | 0.2897 | 0.0668 | 76.95 |
| B0007 | middle | 84 | 1.6109 | 1.5987 | 0.0888 | 0.0042 | 95.26 |
| B0007 | late | 168 | 1.4325 | 1.4675 | 0.1483 | 0.0134 | 90.94 |
| B0018 | middle | 66 | 1.5316 | 1.5849 | 0.1082 | 0.0198 | 81.73 |
| B0018 | late | 132 | 1.3411 | 1.3933 | 0.1756 | 0.0219 | 87.54 |
## 6. Conclusion

This study evaluated FGO-based SOC estimation under battery aging conditions using public NASA lithium-ion battery aging datasets. Unlike simulation-only studies, this work used experimentally measured discharge data and reconstructed reference SOC trajectories based on measured discharge capacity. Battery B0005 was first used as the main representative case to establish the preprocessing, baseline evaluation, and FGO-based estimation workflow. The proposed workflow was then extended to B0006, B0007, and B0018 for cross-cell validation.

The results show that capacity degradation has a significant impact on SOC estimation when the battery capacity is assumed to be constant. Nominal-capacity Coulomb Counting produced increasing SOC errors as the battery aged. For B0005, the RMSE increased to 0.1041 in the middle aging stage and 0.1881 in the late aging stage. Similar trends were observed in the other NASA cells, especially B0006, which exhibited stronger capacity degradation.

A fixed-capacity FGO formulation with a voltage factor provided only limited improvement because the capacity was still fixed to the initial value. This indicates that adding a voltage factor alone is insufficient for aged batteries if the dominant effect of capacity degradation is not explicitly considered.

To address this limitation, a physically constrained capacity-aware FGO formulation was introduced. In this formulation, the SOC trajectory is generated from the cumulative discharged capacity and an estimated effective capacity. This design enforces a monotonic SOC decrease during discharge and avoids non-physical SOC recovery. The proposed method significantly reduced SOC estimation errors in the middle and late aging stages. Across B0005, B0006, B0007, and B0018, the physically constrained capacity-aware FGO consistently outperformed nominal-capacity Coulomb Counting.

The proposed approach demonstrates that FGO is useful not only as a state estimation framework, but also as a flexible structure for incorporating physical constraints and aging-related parameters. The results suggest that capacity-aware FGO can be a promising component for future aging-aware battery management systems and battery digital twin applications.

This study still has several limitations. The reference SOC was reconstructed from discharge capacity rather than directly measured internal SOC. The voltage-SOC relationship was modeled using a simple empirical polynomial fitted from early-stage data. In addition, the current validation was based on selected representative cycles from public experimental datasets. Future work should consider more advanced electrochemical or equivalent-circuit voltage models, online capacity estimation under partial discharge conditions, and broader validation using additional real-world driving profiles and battery datasets.

