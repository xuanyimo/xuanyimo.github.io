---
layout: post
title: "SpringBoot配置文件中配置的提示设置"
data: 2017-09-10 20:17:00 +0800
description: 使用SpringBootConfigurationProcessor设置application配置文件的提示
categories: [SpringBoot]
tag: [Spring, Spring-Boot, Java, Configuration]
---

* Kramdown table of contents
{:toc .toc}

> `SpringBoot`版本为`2.1.5.RELEASE`
`Java`为`1.8`

# 依赖

{% highlight xml %}
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-configuration-processor</artifactId>
    <optional>true</optional>
</dependency>
{% endhighlight %}

# 通过注解设置

{% highlight java %}
// 1. 启用属性配置
@EnableConfigurationProperties

// 2. 在Bean上指定配置
@ConfigurationProperties(prefix = "xxx")

// 3. 对应`Bean`里加入`getters`, `setters`

// 4. 如果有嵌套在字段里的类时使用
@NestedConfigurationProperty
{% endhighlight %}

--- 

## 例子

{% highlight java %}
@ConfigurationProperties("demo2")
@Data
public class ConfigAnnotation {
    private FirstNameEnum firstName;
    private String lastName;
}

public enum FirstNameEnum {
    FIRST_NAME_1,
    FIRST_NAME_2
}

// 在SpringBootApplication或者其它地方上加入@EnableConfigurationProperties
{% endhighlight %}

在`application.yaml`中的效果为

<img src="{{ site.baseurl }}/assets/images/spring-configuration-processor/spring-config-processor-annotation-0.png" style="width: 100%">

<img src="{{ site.baseurl }}/assets/images/spring-configuration-processor/spring-config-processor-annotation-1.png" style="width: 100%">

***嵌套类***

******{% highlight java %}
@Data
@ConfigurationProperties("demo")
public class ConfigSetting {
    @NestedConfigurationProperty
    private ConfigInner inner;

    @Data
    public static class ConfigInner {
        private String innerName;
    }
}
{% endhighlight %}

--- 

# 通过配置JSON文件来配置

在`resources`文件夹下新建文件`META-INF/additional-spring-configuration-metadata.json`

<img src="{{ site.baseurl }}/assets/images/spring-configuration-processor/spring-config-processor-json-0.png">

文件里有三个`key`
1. `groups`
2. `properties`
3. `hints`


## groups 和 properties

`groups`和`properties`都为`org.springframework.boot.configurationprocessor.metadata.ItemMetadata`
{% highlight java %}
public final class ItemMetadata implements Comparable<ItemMetadata> {

	private ItemType itemType;

	private String name;

	private String type;

	private String description;

	private String sourceType;

	private String sourceMethod;

	private Object defaultValue;

	private ItemDeprecation deprecation;
...
}
{% endhighlight %}
`ItemType` 分为 `gruops`和`property`两种
### `groups`
`name`: 组名字，必需项
`type`: 数据类型，即配置项对应类
`description`: 描述
`sourceType`: 如果`@ConfigurationProperties`加在一个`@Bean`方法上，刚这个方法所在的类为`sourceType`，如下的为`${package}.Config`
`sourceMethod`: 如果`@ConfigurationProperties`加在一个`@Bean`方法上，刚这个方法为`sourceMethod`，如下的为`configSetting()`
@Configuration
public class Config {
  @Bean
  @ConfigurationProperties("demo")
  public ConfigSetting configSetting() {
    return new ConfigSetting();
  }
}

### `properties`
`name`: 属性名
`type`: 属性数据类型
`sourceType`: 所在类，如果`@ConfigurationProperties`加在一个`@Bean`方法上，刚这个方法所在的类为`sourceType`
`description`: 描述
`defaultValue`: 默认值，这个只是提示，**并不是真的默认值**
`deprecation`: 废弃使用
  `level`: error（在IDE里会提示错误）, warning（只会有警告）
  `reason`: 废弃原因
  `replacement`: 替代属性

## hints
`name`: 属性名
`values`: 可选值，是一个`org.springframework.boot.configurationprocessor.metadata.ItemHint$ValueHint`数组
  `name`: 名称
  `value`: 值
`providers`: 有以下几个值
  `any`: 可以是任何附加值
  `class-reference`: 会提示输入一个指定的类型
  `handle-as`: 作为某种类型来处理，如文件，枚举，编码，语言，MimeType
  `logger-name`: 提示为日志名字，类似于logging.level
  `spring-bean-reference`: 自动补全定义在这个工程中的Bean
  `spring-profile-name`: 自动补全定义在这个工程中的profile

## 例子

### 常用
{% highlight json %}
{"groups": [
	{
		"name": "server",
		"type": "org.springframework.boot.autoconfigure.web.ServerProperties",
		"sourceType": "org.springframework.boot.autoconfigure.web.ServerProperties"
	},
	{
		"name": "spring.jpa.hibernate",
		"type": "org.springframework.boot.autoconfigure.orm.jpa.JpaProperties$Hibernate",
		"sourceType": "org.springframework.boot.autoconfigure.orm.jpa.JpaProperties",
		"sourceMethod": "getHibernate()"
	}
	...
],"properties": [
	{
		"name": "server.port",
		"type": "java.lang.Integer",
		"sourceType": "org.springframework.boot.autoconfigure.web.ServerProperties"
	},
	{
		"name": "server.address",
		"type": "java.net.InetAddress",
		"sourceType": "org.springframework.boot.autoconfigure.web.ServerProperties"
	},
	{
		  "name": "spring.jpa.hibernate.ddl-auto",
		  "type": "java.lang.String",
		  "description": "DDL mode. This is actually a shortcut for the \"hibernate.hbm2ddl.auto\" property.",
		  "sourceType": "org.springframework.boot.autoconfigure.orm.jpa.JpaProperties$Hibernate"
	}
	...
],"hints": [
	{
		"name": "spring.jpa.hibernate.ddl-auto",
		"values": [
			{
				"value": "none",
				"description": "Disable DDL handling."
			},
			{
				"value": "validate",
				"description": "Validate the schema, make no changes to the database."
			},
			{
				"value": "update",
				"description": "Update the schema if necessary."
			},
			{
				"value": "create",
				"description": "Create the schema and destroy previous data."
			},
			{
				"value": "create-drop",
				"description": "Create and then destroy the schema at the end of the session."
			}
		]
	}
]}
{% endhighlight %}

### hints providers

#### `any`就是可以写任何值，没有提示

#### `class-reference`
{% highlight json %}
{"hints": [
	{
		"name": "server.servlet.jsp.class-name",
		"providers": [
			{
				"name": "class-reference",
				"parameters": {
					"target": "javax.servlet.http.HttpServlet"
				}
			}
		]
	}
]}
{% endhighlight %}

#### `handle-as`
可选类型为
1. `java.nio.charset.Charset` (UTF-8)
2. `java.util.Locale` (en_US)
3. `org.springframework.util.MimeType` (text/plain)
4. `org.springframework.core.io.Resource` (classpath:/sample.properties)

{% highlight json %}
{"hints": [
	{
		"name": "spring.liquibase.change-log",
		"providers": [
			{
				"name": "handle-as",
				"parameters": {
					"target": "org.springframework.core.io.Resource"
				}
			}
		]
	}
]}
{% endhighlight %}

#### `logger-name`
{% highlight json %}
{"hints": [
	{
		"name": "logging.level.keys",
		"values": [
			{
				"value": "root",
				"description": "Root logger used to assign the default logging level."
			},
			{
				"value": "sql",
				"description": "SQL logging group including Hibernate SQL logger."
			},
			{
				"value": "web",
				"description": "Web logging group including codecs."
			}
		],
		"providers": [
			{
				"name": "logger-name"
			}
		]
	},
	{
		"name": "logging.level.values",
		"values": [
			{
				"value": "trace"
			},
			{
				"value": "debug"
			},
			{
				"value": "info"
			},
			{
				"value": "warn"
			},
			{
				"value": "error"
			},
			{
				"value": "fatal"
			},
			{
				"value": "off"
			}

		],
		"providers": [
			{
				"name": "any"
			}
		]
	}
]}
{% endhighlight %}

#### `spring-bean-reference`
{% highlight json %}
{"hints": [
	{
		"name": "spring.jmx.server",
		"providers": [
			{
				"name": "spring-bean-reference",
				"parameters": {
					"target": "javax.management.MBeanServer"
				}
			}
		]
	}
]}
{% endhighlight %}

#### `spring-profile-name`
{% highlight json %}
{"hints": [
	{
		"name": "spring.profiles.active",
		"providers": [
			{
				"name": "spring-profile-name"
			}
		]
	}
]}
{% endhighlight %}

