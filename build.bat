@echo off
::REM 构建测试数据
python DataSeeder.py && python GoodCases.py
@echo on