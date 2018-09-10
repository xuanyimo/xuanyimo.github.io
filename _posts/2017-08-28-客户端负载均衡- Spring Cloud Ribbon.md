---
layout: post
title: "客户端负载均衡: Spring Cloud Ribbon" 
img: spring-cloud.png
date: 2017-08-28 23:34:00 +0800
description: 对Spring Cloud Ribbon的研究
tag: [Spring, Spring-Cloud, Java, Ribbon]
categories: [SpringCloud]
--- 

* 
{:toc .toc}

# RestTemplate 详解

## GET 请求

### 1. `getForEntity`

{% highlight java %}
// 1. 返回http响应中的一些关键信息(HttpStatus, HttpHeaders, HttpEntity)
// 方法1
ResponseEntity<T> getForEntity(String url, Class<T> responseType, Object... urlVariables);
// 方法2
ResponseEntity<T> getForEntity(String url, Class<T> responseType, Map<String, ?> urlVariables);
// 方法3
ResponseEntity<T> getForEntity(URI uri, Class<T> responseType);

// eg: 实现方法1
ResponseEntity<String> responseEntity = restTemplate.getForEntity("http://service/string?param={1}", String.class, "paramValue1");
// eg: 实现方法2
ResponseEntity<String> responseEntity = restTemplate.getForEntity("http://service/string?param={1}", String.class, "paramValue1");
{% endhighlight %}

### 2. `getForObject`

{% highlight java %}
// 同Get请求中1的重载，只是直接返回了body
T getForObject(String url, Class<T> responseType, Object... urlVariables);
T getForObject(String url, Class<T> responseType, Map<String, ?> urlVariables);
T getForObject(URI uri, Class<T> responseType);

// eg: 实现方法1
String result = restTemplate.getForObject(url, String.class, "value1");
{% endhighlight %}



## POST请求

### 1. `postForEntity`

{% highlight java %}
// 同Get请求中1的重载，只是直接返回了body
T postForEntity(String url, Class<T> responseType, Object... urlVariables);
T postForEntity(String url, Class<T> responseType, Map<String, ?> urlVariables);
T postForEntity(URI uri, Class<T> responseType);

{% endhighlight %}



### 2. `postForObject`

{% highlight java %}
// 同Get请求中1的重载，只是直接返回了body
T postForObject(String url, Class<T> responseType, Object... urlVariables);
T postForObject(String url, Class<T> responseType, Map<String, ?> urlVariables);
T postForObject(URI uri, Class<T> responseType);

{% endhighlight %}

### 3. `postForLocation`

> 该方法返回新资源的URI (相当于指定的返回类型是URI)

{% highlight java %}

URI postForLocation(String url, Object request, Object… urlVariables);

URI postForLocation(String url, Object request, Map<String, ?> urlVariables);

URI postForLocation(URI uri, Object request);

{% endhighlight %}

## PUT请求

{% highlight java %}

void put(String url, Object request, Object… urlVariables);

void put(String url, Object request, Map<String, ?> urlVariables);

void put(URI uri, Object request);

{% endhighlight %}

### DELETE请求

> itompotent

{% highlight java %}

void delete(String url, Object request,  Object… urlVariables);

void delete(String url, Object request, Map<String, ?> urlVariables);

void delete(URI uri, Object request);

{% endhighlight %}



> Tips: 顺便复习一下HttpMethod的安全与幂等
<div id="datatable-begin"></div>

 | HttpMethod | Safe | Idempotent |
 |:--------|:----:|:----------:|
 | GET     | √    | √          |
 | HEAD    | √    | √          |
 | OPTIONS | √    | √          |
 | PUT     | x    | √          |
 | DELETE  | √    | x          |
 | POST    | x    | x          |
 | PATCH   | x    | x          |

<div id="datatable-end"></div>

 

# 负载均衡器


