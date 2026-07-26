MetaCar Hybrid 安装指南
==========================

系统要求
--------

* Python 3.10 或更高版本
* 网络连接，用于与服务器通信

通过 pip 安装
---------------

推荐在虚拟环境中安装 MetaCar Hybrid。
本产品使用独立的 ``metacar_hybrid`` Python 导入包名，
可以与原版 ``metacar`` 安装在同一个环境中。

.. code-block:: bash

    python -m pip install metacar-hybrid

安装虚实结合示例依赖：

.. code-block:: bash

    python -m pip install "metacar-hybrid[examples]"

从源码安装
----------

您也可以通过克隆代码仓库并安装的方式获取最新开发版本：

.. code-block:: bash

    git clone https://github.com/YDL-Simulation/metacar-hybrid.git
    cd metacar-hybrid
    python -m pip install -e ".[examples]"

依赖项
------

MetaCar 依赖以下库，在安装过程中会自动安装：

* OpenCV (cv2) - 用于图像处理
* NumPy - 用于科学计算
* Pydantic - 用于数据模型

验证安装
--------

安装完成后，可以通过导入库来验证安装是否成功：

.. code-block:: python

    import metacar_hybrid
    print(metacar_hybrid.__version__)
