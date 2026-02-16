# HPL解析器修复计划

## 问题
HPL解析器无法正确处理三层及以上嵌套属性访问（如 `player_config.warrior.description`）

## 修复步骤

1. [ ] 查看 models.py 了解现有模型定义
2. [ ] 创建 PropertyAccess 类用于属性访问（区别于 MethodCall）
3. [ ] 修改 ast_parser.py 中的 `_parse_method_chain_expr` 方法
4. [ ] 修改 ast_parser.py 中的 `_parse_expression_suffix` 方法
5. [ ] 修改 evaluator.py 支持 PropertyAccess 的求值
6. [ ] 测试修复后的解析器

## 状态
- [x] 问题分析完成
- [ ] 修复实施中
