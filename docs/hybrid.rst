MetaCar Hybrid 虚实结合控制
==================================

MetaCar Hybrid 在原有 MetaCar 通信模型上增加 ``HybridControl`` 数据，
用于在虚实结合场景中接收平台时间步并发送 Delta 位移控制。

安装
----

MetaCar Hybrid 使用独立的 ``metacar_hybrid`` Python 导入包名，
可以与原版 ``metacar`` 安装在同一个虚拟环境中。

.. code-block:: bash

   python -m pip install --pre metacar-hybrid

接收 HybridControl
------------------

``main_loop()`` 返回的 ``SimCarMsg`` 中可通过 ``hybrid_control``
读取平台发送的混合控制信息。

.. code-block:: python

   hybrid_control = sim_car_msg.hybrid_control or {}
   dt = hybrid_control.get("deltaTime")

当平台未发送 ``HybridControl`` 时，``hybrid_control`` 为 ``None``。
基础运行程序在 ``deltaTime`` 缺失或无效时，会使用经过上下限保护的
本机循环时间作为回退，避免程序只能发送零位移。

发送 Delta 控制
----------------

.. code-block:: python

   api.set_hybrid_delta(dx=0.1, dy=0.0, dt=dt)

``dx`` 和 ``dy`` 的单位及坐标系应与当前虚实平台协议保持一致。
``dt`` 可选；传入时将序列化为 ``HybridControl.deltaTime``。

完整示例
--------

.. code-block:: python

   from metacar_hybrid import SceneAPI

   api = SceneAPI()
   api.connect()

   for sim_car_msg, frames in api.main_loop():
       hybrid_control = sim_car_msg.hybrid_control or {}
       dt = hybrid_control.get("deltaTime")

       dx = 0.1
       dy = 0.0
       api.set_hybrid_delta(dx=dx, dy=dy, dt=dt)

可公开的基础键盘 Delta 控制示例位于
``examples/main_hybrid_basic.py``。它作为独立应用只调用 ``SceneAPI`` 等稳定
SDK 接口，自行实现连接、主循环、键盘控制、状态输出、停车、重开、跳关和
安全退出所需的完整基础流程。完整轨迹跟踪和产品测试策略不包含在对外发布包中。
