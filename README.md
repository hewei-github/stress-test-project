微信搜索压测脚本项目
=======================

> ## 1. 微信搜索开发过程

**微信测试都使用正式小程序环境,不是体验服,数据量只有几百条记录的提审环境是过不了,
不同环境的结果id,跳转不匹配,垃圾数据无法使用(质量问题),请开发人员注意**

1. 配置好微信后台与微信搜索相关配置(开发接口,搜索模型协议选择)  
2. 准备好数据接入,初始化一批数据(按照微信要求上传相关数据模型所需的数据集,数据量要过3000,少量数据可能不会通过)  
3. 数据初始化通关后准备搜索业务模型功能开发  
4. 通关业务工具做好压测和自测(本工具所处位置)   
  
   注意: 微信压测是要申请的，申请他有固定的时段进行压测  
   由于压测注意测试搜索服务接口的质量 和 请求速度 , 并发量大。
   请在何时时间段内申请压测(不影响线上系统,用户量少的时间段,建议在下午)
   为了应对并发查询，建议使用缓存(redis) + 搜索引擎 (ElasticSearch), 
   本工具后端接口在实现过程中使用了以上2种技术，完美通过高并发查询(230ms)内响应  
      
5. 压测通后,还有视图测试，也就是前端逻辑和数据正确性的问题，还有结构一致性排查 
   
   举例 :  
        提交 测测试数据 + 数据落地页结果截图 说明的内容文件(提测PDF文件-tip:word转pdf)
        上传给微信(公众号后台微信搜索)  
        
   微信测试人员 将在 1-3 (测试时段不定,请准备号环境)个作日内给出测试反馈(通过 或 不通过原因)不通过原因 :   
          
          1. 搜索内容不符   
          2. 内容和落地页不符(与文档中不符，与实际情况不符)   
          3. 落地页异常或者空白  
          4. 搜索不出提测文件中的结果  
          5. 前端跳转排序不符(这个需要前端和api 配置)               
          
6. 压缩，前端测试(视图测试) 通过后 ， 就到了申请上线阶段，请注意不要到最后一步垮了

    1. 环境问题  
        由于申请上线测试人员是不定时间检查的，他还会再测试一下之前的数据和界面  
        运气不好，环境切换了，获取的id 跳转到前端可能就会异常或者空白 
     
    2. 数据上下架数量过大 
        还是上面的问题，抽查的人不会那么好心随便让你过(搜索不到之前测试相关的结果)     
    
    3. 不要随便修改微信后台微信搜索接口api地址(微信后台限制,一个月内修改次数有限)  
    
    4. 返回的数据结构不要随便修改,结构不对 微信搜索展示会异常  
    
    5. 请注意申请上线的审核人员 审核时间不定 ，备好一周的不发版(不切换环境的)准备  

7. 为啥要注意环境 , 因为微信搜索提供的业务通知接口只能填一个，且是微信通知你，微信搜一搜界面是不会有环境区分的
  
  
>  ## 2.工具脚本使用说明  
  
  1. 使用 export_source.sql 导出相关 json 数据保存到config目录 (为何是json->方便使用),请注意看export_source.sql 中的说明    
  2. 去微信后台调试工具页页面手动调试 一次 微信搜索事件通知, 抓取对应的 cookie 值 替换config/cookie.json 中过期的旧数据    
  3. 安装好工具所需要的依赖 (工具包括通过数据源data.json 生成测试所需数据,压测工具, 自动分析收集最优测试用例 )  
  ```bash
    $ pip install -r requirements.txt 
  ```  
  4. 运行 build.sh (win 平台运行 build.bat) 构建测试用例    
  5. 运行 start.py (启动压测功能,压测工具自带简易web界面)  
  6. 在压测工具的web 界面中选择压测模拟请求数量 和 压测时间    
  7. 等待,压测完毕, storage 目录下收集了 目前可用用类 data.good.case    
  8. 将可用用例文件 拷贝一份 ,修改成 test_case.txt ,并将第一行内容 "[#data]" (非json内容删除)    
  9. 将test_case.txt 上传到微信相关压测表单中, 还有对应 自测通过率 结果pdf(ps:计算或者估值也行,一行数据表格pdf总结就行,参照demo目录下的demo_stress.pdf) 一并上传    
  10. 申请提交时，选择好对应时间和时段，准备压测  
  11. 预防压测失败，可以先使用 start.py (在测试时间到来之前1个小时)进行数据预预热    


> ## 3. 视图测试请参照相关 demo/demo.doc 

