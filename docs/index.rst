.. Metacar documentation master file, created by
   sphinx-quickstart on Fri Apr  4 16:13:57 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

欢迎使用 MetaCar Hybrid 文档
=============================

MetaCar Hybrid 是面向智能网联汽车虚实结合场景的 Python API，
用于与场景平台通信、获取车辆状态并发送虚实结合控制量。

.. toctree::
   :maxdepth: 2
   :caption: 目录:

   installation
   quickstart
   hybrid
   api/index
   examples
   vla

特性
----

* 支持与仿真环境的 TCP 通信
* 提供向量计算、几何变换等实用工具
* 丰富的数据模型，支持无缝解析与使用
* 支持流式视频图像的获取和处理
* 支持 ``HybridControl`` 解析和 Delta 位移控制
