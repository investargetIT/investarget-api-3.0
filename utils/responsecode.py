#coding=utf-8
responsecode = {
    '1000':'请求成功',
    '9999':'没标明状态码的错误',
    '8888':'unavailable source',
    '8889':'用户未登录',
    '8890':'give obj but expect queryset',
    '8891':'字段名错误',

    '2001':'密码错误',
    '2002':'用户不存在',
    '20021':'用户审核未通过',
    '2003':'登录类型不可用',
    '2004':'账号已存在',
    '20041':'手机号已存在',
    '20042':'邮箱已存在',
    '2005':'验证码错误',
    '20051':'验证码过期',
    '2007':'mobile、email不能都为空',
    '20071':'请求参数有误',
    '20072':'参数缺失',
    '2008':'该组别下有用户存在，不能删除',

    '2009':'没有权限',
    '20091':'没有权限修改部分字段信息',
    '2010':'删除项有关联数据',

    '2011':'用户关系不存在',
    '2012':'用户关系已存在',
    '2013':'强关系只能有一个',
    '2014':'不能在两个相同的人之间建立关系',
    '2015':'建立关系的用户没有相应的权限(as_投资人或as_交易师)',
    '2016':'不能和自己成为好友',
    '2017':'已存在好友关系',
    '2018':'站内信收信人不能为空',
    '2019':'站内信新增失败',
    '2020':'文件上传失败',
    '2021':'bucket有误',
    '2022':'用户审核未通过',
    '2023':'聊天账号注册失败',
    '2024':'离职人员无法成为BD负责人',
    '2025':'账号尚在保护期内，无法再次增加交易师',

    '3000':'token验证失败',
    '30011':'短信发送失败',
    '30012':'国际短信发送失败',
    '3002':'邮件发送失败',
    '3003':'ip获取失败',
    '3004':'请求频率太高，请稍后重试',
    '3005':'禁止访问',
    '3006':'未检测到ip地址',
    '3007':'非法客户端',

    '4001':'上传项目信息有误',
    '4002':'项目不存在',
    '4003':'项目财务信息有误',
    '40031':'财务信息不再存在',
    '4004':'隐藏项目，没有权限查看',
    '4005':'项目收藏类型错误（没有该类型权限）',
    '4006':'项目收藏id不存在',
    '4007':'项目信息未完善，无法终审发布',
    '4008':'pdf生成失败',
    '4009':'项目BD记录生成失败',

    '5001':'机构证券代码（stockcode）已存在',
    '5002':'机构不存在',
    '5003':'项目尚未终审发布',
    '5004':'项目BD记录生成失败',
    '5005':'会议BD生成失败',
    '5006':'该用户已存在一条BD记录',
    '5007':'该用户已存在一条相同记录',


    '6001':'时间轴状态重复（不唯一），数据库数据有误',
    '6002':'时间轴不存在',
    '60021':'时间轴备注不存在',
    '6003':'已经存在一个相同的时间轴了',
    '6004':'时间轴已关闭，不能修改状态',

    '7001':'dataroom已存在',
    '7002':'dataroom不存在或已被删除',
    '7003':'dataroom 角色不合法',
    '7004':'dataroom创建数据缺失',

    '7006':'删除目录不为空',
    '7007':'类型错误',
    '7008':'删除文件（目录）有复制体存在',
    '7009':'复制体（目录/文件）不允许操作',
    '7010':'删除失败',
    '7011':'不能移动或复制到该dataroom下',
    '7012':'dataroom已关闭，无法增加内容',
    '7013':'用户已存在一个相同项目的dataroom了',

    '8001':'项目公司已存在',
    '8002':'文件不存在',
    '8003':'记录不存在',
    '8004':'正在准备压缩文件',
    '8005':'压缩已完成',
}
