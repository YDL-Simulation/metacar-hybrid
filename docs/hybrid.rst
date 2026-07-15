MetaCar Hybrid 虚实结合控制
==================================

MetaCar Hybrid 在原有 MetaCar 通信模型上增加 ``HybridControl`` 数据，
用于在虚实结合场景中接收平台时间步并发送 Delta 位移控制。

安装
----

MetaCar Hybrid 与原版 ``metacar`` 使用相同的 Python 导入包名，
两者不应安装在同一个虚拟环境中。

.. code-block:: bash

   python -m pip uninstall -y metacar
   python -m pip install metacar-hybrid

接收 HybridControl
------------------

``main_loop()`` 返回的 ``SimCarMsg`` 中可通过 ``hybrid_control``
读取平台发送的混合控制信息。

.. code-block:: python

   hybrid_control = sim_car_msg.hybrid_control or {}
   dt = hybrid_control.get("deltaTime")

当平台未发送 ``HybridControl`` 时，``hybrid_control`` 为 ``None``。

发送 Delta 控制
----------------

.. code-block:: python

   api.set_hybrid_delta(dx=0.1, dy=0.0, dt=dt)

``dx`` 和 ``dy`` 的单位及坐标系应与当前虚实平台协议保持一致。
``dt`` 可选；传入时将序列化为 ``HybridControl.deltaTime``。

完整示例
--------

.. code-block:: python

   from metacar import SceneAPI

   api = SceneAPI()
   api.connect()

   for sim_car_msg, frames in api.main_loop():
       hybrid_control = sim_car_msg.hybrid_control or {}
       dt = hybrid_control.get("deltaTime")

       dx = 0.1
       dy = 0.0
       api.set_hybrid_delta(dx=dx, dy=dy, dt=dt)

可公开的基础键盘 Delta 控制示例位于
``examples/main_hybrid_basic.py``，安装示例依赖后也可以通过
``metacar-hybrid-basic`` 命令运行。完整轨迹跟踪和产品测试策略不包含在对外发布包中。
