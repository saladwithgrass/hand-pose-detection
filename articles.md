# Реконструкция сцены
## База про триангуляцию
@phdthesis{sombekke2020triangulation,
  title={Triangulation for depth estimation},
  author={Sombekke, Niels and Visser, Arnoud},
  year={2020},
  school={University of Amsterdam Amsterdam, The Netherlands}
}

## Три принципа стерео зрения
Здесь описываются основы реконструкции и триангуляции.
@article{Sugihara01011986,
author = {Kokichi Sugihara and},
title = {Three principles in stereo vision},
journal = {Advanced Robotics},
volume = {1},
number = {4},
pages = {391--400},
year = {1986},
publisher = {Taylor \& Francis},
doi = {10.1163/156855386X00256},
URL = {https://doi.org/10.1163/156855386X00256},
eprint = { https://doi.org/10.1163/156855386X00256 }
}

## Прикольный метод реконструкции
Метод реконструкции сцены, а не точки.
@inproceedings{10.5555/645317.756415,
author = {Kolmogorov, Vladimir and Zabih, Ramin},
title = {Multi-camera Scene Reconstruction via Graph Cuts},
year = {2002},
isbn = {3540437460},
publisher = {Springer-Verlag},
address = {Berlin, Heidelberg},
abstract = {We address the problem of computing the 3-dimensional shape of an arbitrary scene from a set of images taken at known viewpoints. Multi-camera scene reconstruction is a natural generalization of the stereo matching problem. However, it is much more difficult than stereo, primarily due to the difficulty of reasoning about visibility. In this paper, we take an approach that has yielded excellent results for stereo, namely energy minimization via graph cuts. We first give an energy minimization formulation of the multi-camera scene reconstruction problem. The energy that we minimize treats the input images symmetrically, handles visibility properly, and imposes spatial smoothness while preserving discontinuities. As the energy function is NP-hard to minimize exactly, we give a graph cut algorithm that computes a local minimum in a strong sense. We handle all camera configurations where voxel coloring can be used, which is a large and natural class. Experimental data demonstrates the effectiveness of our approach.},
booktitle = {Proceedings of the 7th European Conference on Computer Vision-Part III},
pages = {82–96},
numpages = {15},
series = {ECCV '02}
}

## Обзор ML методов реконструкции
@ARTICLE{9233988,
  author={Laga, Hamid and Jospin, Laurent Valentin and Boussaid, Farid and Bennamoun, Mohammed},
  journal={IEEE Transactions on Pattern Analysis and Machine Intelligence}, 
  title={A Survey on Deep Learning Techniques for Stereo-Based Depth Estimation}, 
  year={2022},
  volume={44},
  number={4},
  pages={1738-1764},
  keywords={Estimation;Videos;Deep learning;Three-dimensional displays;Australia;Training;Pipelines;CNN;deep learning;3D reconstruction;stereo matching;multi-view stereo;disparity estimation;feature leaning;feature matching},
  doi={10.1109/TPAMI.2020.3032602}}

## RGB-D камеры
@inproceedings{zollhofer2018state,
  title={State of the art on 3D reconstruction with RGB-D cameras},
  author={Zollh{\"o}fer, Michael and Stotko, Patrick and G{\"o}rlitz, Andreas and Theobalt, Christian and Nie{\ss}ner, Matthias and Klein, Reinhard and Kolb, Andreas},
  booktitle={Computer graphics forum},
  volume={37},
  number={2},
  pages={625--652},
  year={2018},
  organization={Wiley Online Library}
}

## Еще что-то про RGB-D
@article{liu2015detecting,
  title={Detecting and tracking people in real time with RGB-D camera},
  author={Liu, Jun and Liu, Ye and Zhang, Guyue and Zhu, Peiru and Chen, Yan Qiu},
  journal={Pattern Recognition Letters},
  volume={53},
  pages={16--23},
  year={2015},
  publisher={Elsevier}
}

# Системы телеоперации
## Обзор на телеоперацию в принципе
Описание того, что такое телеоперация.
Здесь обозреваются способы телеоперации и главные проблемы.
https://pure.tue.nl/ws/portalfiles/portal/4419568/656592.pdf
@article{lichiardopol2007survey,
  title={A survey on teleoperation},
  author={Lichiardopol, S},
  year={2007},
  publisher={Technische Universiteit Eindhoven}
}
## Обзор модельной телеоперации
Здесь описаны общие проблемы телеоперации, также предложен способ уменьшения задержки при телеоперации.
https://ieeexplore.ieee.org/abstract/document/7381599
@ARTICLE{7381599,
  author={Xu, Xiao and Cizmeci, Burak and Schuwerk, Clemens and Steinbach, Eckehard},
  journal={IEEE Access}, 
  title={Model-Mediated Teleoperation: Toward Stable and Transparent Teleoperation Systems}, 
  year={2016},
  volume={4},
  number={},
  pages={425-449},
  keywords={Delays;Teleoperation;Haptic interfaces;Stability analysis;Computer architecture;Impedance;Computational modeling;TIme delay;Model-mediated teleoperation;tele-haptics;time-delayed teleoperation;stability and transparency;parameter estimation;haptic data reduction;model update;Model-mediated teleoperation;tele-haptics;time-delayed teleoperation;stability and transparency;parameter estimation;haptic data reduction;model update},

  doi={10.1109/ACCESS.2016.2517926}}

# Распознавание жестов
## Обзорная статья про распознавание жестов
@ARTICLE{4154947,
  author={Mitra, Sushmita and Acharya, Tinku},
  journal={IEEE Transactions on Systems, Man, and Cybernetics, Part C (Applications and Reviews)}, 
  title={Gesture Recognition: A Survey}, 
  year={2007},
  volume={37},
  number={3},
  pages={311-324},
  keywords={Face recognition;Hidden Markov models;Optical filters;Humans;Arm;Magnetic heads;Manifolds;Handicapped aids;Virtual reality;Filtering;Face recognition;facial expressions;hand gestures;hidden Markov models (HMMs);soft computing;optical flow},
  doi={11.1109/TSMCC.2007.893280}}

# ТУПА Я
@ARTICLE{1512452,
  author={Kofman, J. and Xianghai Wu and Luu, T.J. and Verma, S.},
  journal={IEEE Transactions on Industrial Electronics}, 
  title={Teleoperation of a robot manipulator using a vision-based human-robot interface}, 
  year={2005},
  volume={52},
  number={5},
  pages={1206-1219},
  keywords={Robot vision systems;Humans;Manipulator dynamics;Robot control;Mechanical sensors;Shape control;Intelligent robots;Mechanical engineering;Design engineering;Systems engineering and theory;Human–robot interface;real time;robot manipulator;semi-autonomous control;teleoperation;traded and shared control;vision-based tracking},
  doi={10.1109/TIE.2005.855696}}

