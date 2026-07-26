# 上游兼容记录

MetaCar Hybrid 是基于 [YDL-Simulation/autodrive_api_python](https://github.com/YDL-Simulation/autodrive_api_python) 的独立产品。本文件记录每个 MetaCar Hybrid 版本所使用的上游基线。

## MetaCar Hybrid 0.1.0

- 上游标签：`v0.4.0`
- 上游提交：`7e468c911f9f655784dfd1288227a2672fc073f0`
- 上游仓库：`https://github.com/YDL-Simulation/autodrive_api_python`
- 产品增量：稳定 `metacar_hybrid` 独立命名空间、虚实结合通信与 Delta 控制公开 API，并保持基础控制示例与 SDK 发布包解耦

## MetaCar Hybrid 0.1.0a4

- 上游标签：`v0.4.0`
- 上游提交：`7e468c911f9f655784dfd1288227a2672fc073f0`
- 上游仓库：`https://github.com/YDL-Simulation/autodrive_api_python`
- 产品增量：基础示例连接顺序与 `main.py` 对齐，增加控制端口、视频端口和初始化握手状态提示

## MetaCar Hybrid 0.1.0a3

- 上游标签：`v0.4.0`
- 上游提交：`7e468c911f9f655784dfd1288227a2672fc073f0`
- 上游仓库：`https://github.com/YDL-Simulation/autodrive_api_python`
- 产品增量：提供可直接运行的基础键盘控制程序、退出处理和 `deltaTime` 回退

## MetaCar Hybrid 0.1.0a2

- 上游标签：`v0.4.0`
- 上游提交：`7e468c911f9f655784dfd1288227a2672fc073f0`
- 上游仓库：`https://github.com/YDL-Simulation/autodrive_api_python`
- 产品增量：将 Python 包重命名为 `metacar_hybrid`，支持与原版 `metacar` 同环境共存

## MetaCar Hybrid 0.1.0a1

- 上游标签：`v0.4.0`
- 上游提交：`7e468c911f9f655784dfd1288227a2672fc073f0`
- 上游仓库：`https://github.com/YDL-Simulation/autodrive_api_python`
- 产品增量：`HybridControl` 接收模型、Delta 控制发送和可公开的基础键盘控制示例

## 同步原则

1. 通过 `git fetch upstream --tags` 获取上游更新。
2. 在 `sync/upstream-<tag-or-commit>` 分支中合并和测试。
3. 不在已发布的产品主分支上强制 rebase。
4. 优先保留上游安全修复、通信修复和数据模型修复。
5. 合并后更新本文件、测试和发布说明。
