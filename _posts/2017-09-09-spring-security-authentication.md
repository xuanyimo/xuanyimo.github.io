---
layout: post
title: spring-scurity-authentication code analysis
description: This blog will tell you Spring-Scurity how to auth your identity
date: 2017-09-09 17:04
categories: [Spring]
tag: [Spring-Scurity, Spring]
---

* Kramdown table of contents
{:toc .toc}

> SpringSecurityVersion: 4.2.3.RELEASE

> 分析思路: 探究WebSecurityConfigurerAdapter中的configure(HttpSecurity http)方法是如何生效的。

# `WebSecurityConfiguration`
WebSecurityConfiguration是主要的配置类，其中产生由WebSecurity生成的Filter，之后就可以通过这些Filter来做一些安全验证。

{% highlight java %}
@Autowired(required = false)
public void setFilterChainProxySecurityConfigurer(
		ObjectPostProcessor<Object> objectPostProcessor,
		@Value("#{@autowiredWebSecurityConfigurersIgnoreParents.getWebSecurityConfigurers()}") List<SecurityConfigurer<Filter, WebSecurity>> webSecurityConfigurers)
		throws Exception {
	webSecurity = objectPostProcessor
			.postProcess(new WebSecurity(objectPostProcessor));
	if (debugEnabled != null) {
		webSecurity.debug(debugEnabled);
	}

	Collections.sort(webSecurityConfigurers, AnnotationAwareOrderComparator.INSTANCE);

	Integer previousOrder = null;
	Object previousConfig = null;
	for (SecurityConfigurer<Filter, WebSecurity> config : webSecurityConfigurers) {
		Integer order = AnnotationAwareOrderComparator.lookupOrder(config);
		if (previousOrder != null && previousOrder.equals(order)) {
			throw new IllegalStateException(
					"@Order on WebSecurityConfigurers must be unique. Order of "
							+ order + " was already used on " + previousConfig + ", so it cannot be used on "
							+ config + " too.");
		}
		previousOrder = order;
		previousConfig = config;
	}
	for (SecurityConfigurer<Filter, WebSecurity> webSecurityConfigurer : webSecurityConfigurers) {
		webSecurity.apply(webSecurityConfigurer);
	}
	this.webSecurityConfigurers = webSecurityConfigurers;
}
{% endhighlight %}

在setFilterChainProxySecurityConfigurer中第一行，webSecurity被赋值，ObjectPostProcessor的实现如下:
{% highlight java %}
@Configuration
public class ObjectPostProcessorConfiguration {

	@Bean
	public ObjectPostProcessor<Object> objectPostProcessor(
			AutowireCapableBeanFactory beanFactory) {
		return new AutowireBeanFactoryObjectPostProcessor(beanFactory);
	}
}
{% endhighlight %}

关于ObjectPostProcessor不再说明。

---

下面的代码里(代码片段1)注入了Filter，通过WebSecurity的build方法，可以看到，在这个方法里用到了WebSecurityConfigurerAdapter，appley把adapter这个配置添加到了AbstractConfiguredSecurityBuilder类的configurers和configurersAddedInInitializing中(代码片段2)。(通过调用apply中的add方法)

`代码片段1:`
{% highlight java %}
@Bean(name = AbstractSecurityWebApplicationInitializer.DEFAULT_FILTER_NAME)
public Filter springSecurityFilterChain() throws Exception {
	boolean hasConfigurers = webSecurityConfigurers != null
			&& !webSecurityConfigurers.isEmpty();
	if (!hasConfigurers) {
		WebSecurityConfigurerAdapter adapter = objectObjectPostProcessor
				.postProcess(new WebSecurityConfigurerAdapter() {
				});
		webSecurity.apply(adapter);
	}
	return webSecurity.build();
}
{% endhighlight %}

`代码片段2:`
{% highlight java %}
private <C extends SecurityConfigurer<O, B>> void add(C configurer) throws Exception {
	Assert.notNull(configurer, "configurer cannot be null");

	Class<? extends SecurityConfigurer<O, B>> clazz = (Class<? extends SecurityConfigurer<O, B>>) configurer
			.getClass();
	synchronized (configurers) {
		if (buildState.isConfigured()) {
			throw new IllegalStateException("Cannot apply " + configurer
					+ " to already built object");
		}
		List<SecurityConfigurer<O, B>> configs = allowConfigurersOfSameType ? this.configurers
				.get(clazz) : null;
		if (configs == null) {
			configs = new ArrayList<SecurityConfigurer<O, B>>(1);
		}
		configs.add(configurer);
		this.configurers.put(clazz, configs);
		if (buildState.isInitializing()) {
			this.configurersAddedInInitializing.add(configurer);
		}
	}
}
{% endhighlight %}

---

看一下代码片段1中的webSecurity，最后一行的build方法最终就是由WebSecurity类中performBuild来返回结果的，下面是performBuild的实现。
{% highlight java %}
@Override
protected Filter performBuild() throws Exception {
	Assert.state(
			!securityFilterChainBuilders.isEmpty(),
			"At least one SecurityBuilder<? extends SecurityFilterChain> needs to be specified. Typically this done by adding a @Configuration that extends WebSecurityConfigurerAdapter. More advanced users can invoke "
					+ WebSecurity.class.getSimpleName()
					+ ".addSecurityFilterChainBuilder directly");
	int chainSize = ignoredRequests.size() + securityFilterChainBuilders.size();
	List<SecurityFilterChain> securityFilterChains = new ArrayList<SecurityFilterChain>(
			chainSize);
	for (RequestMatcher ignoredRequest : ignoredRequests) {
		securityFilterChains.add(new DefaultSecurityFilterChain(ignoredRequest));
	}
	for (SecurityBuilder<? extends SecurityFilterChain> securityFilterChainBuilder : securityFilterChainBuilders) {
		securityFilterChains.add(securityFilterChainBuilder.build());
	}
	FilterChainProxy filterChainProxy = new FilterChainProxy(securityFilterChains);
	if (httpFirewall != null) {
		filterChainProxy.setFirewall(httpFirewall);
	}
	filterChainProxy.afterPropertiesSet();

	Filter result = filterChainProxy;
	if (debugEnabled) {
		logger.warn("\n\n"
				+ "********************************************************************\n"
				+ "**********        Security debugging is enabled.       *************\n"
				+ "**********    This may include sensitive information.  *************\n"
				+ "**********      Do not use in a production system!     *************\n"
				+ "********************************************************************\n\n");
		result = new DebugFilter(filterChainProxy);
	}
	postBuildAction.run();
	return result;
}
{% endhighlight %}
在securityFilterChains中添加了一系列的securityFilterChains，在变量securityFilterChainBuilders添加了其他的filterChainBuilder，HttpSecurity的配置也会加到这个地方，
通过HttpSecurity中的addSecurityFilterChainBuilder方法，他是由AbstractConfiguredSecurityBuilder中的init方法调用的。
调用栈为:
{% highlight java %}
webSecurity#build -> 
AbstractSecurityBuilder#doBuild -> 
AbstractConfiguredSecurityBuilder#init -> 
WebSecurityConfigurerAdapter#init ->
WebSecurity#addSecurityFilterChainBuilder
{% endhighlight %}

以下是AbstractSecurityBuilder#doBuild的实现，有多个状态，在init时添加了HttpSecurity到WebSecurity中的FilterChainBuilders中，WebSecurity在执行performBuild时，会调用FilterChainBuilders的build方法，把HttpSecurity生成的DefaultSecurityFilterChain加入到FilterChain中。
{% highlight java %}
@Override
protected final O doBuild() throws Exception {
	synchronized (configurers) {
		buildState = BuildState.INITIALIZING;

		beforeInit();
		init();

		buildState = BuildState.CONFIGURING;

		beforeConfigure();
		configure();

		buildState = BuildState.BUILDING;

		O result = performBuild();

		buildState = BuildState.BUILT;

		return result;
	}
}
{% endhighlight %}

AbstractConfiguredSecurityBuilder#init方法会执行configurers和configurersAddedInInitializing中所有的configure(里面有WebSecurityConfigurerAdapter)的init方法。
以下是WebSecurityConfigurerAdapter#init的源码:
{% highlight java %}
public void init(final WebSecurity web) throws Exception {
	final HttpSecurity http = getHttp();
	web.addSecurityFilterChainBuilder(http).postBuildAction(new Runnable() {
		public void run() {
			FilterSecurityInterceptor securityInterceptor = http
					.getSharedObject(FilterSecurityInterceptor.class);
			web.securityInterceptor(securityInterceptor);
		}
	});
}
{% endhighlight %}
在第二行把HttpSecurity添加到了WebSecurity的securityFilterChainBuilders中，在WebSecurity#performBuild中会build这个chainBuilder(即HttpSecurity)。

---

## 总结

<img src="{{ site.baseurl }}/assets/images/spring-security/web_security_flow.png" style="width: 100%">

> 在WebSecurityConfigurerAdapter中，通过configure配置了HttpSecurity。在WebSecurityConfiguration中会生成一个Filter，这个Filter是由WebSecurity#build产生的，WebSecurity有一个FilterChain，WebSecurity通过performBuild会把HttpSecurity通过performBuild生成的DefaultSecurityFilterChain加入到这个FilterChain中，最后生成的Filter中就会包含HttpSecurity中的配置，在请求时，这个Filter会检验HttpSecurity中的配置。

---

WebSecurity，HttpSecurity都是一系列的安全验证配置，会由SecurityFilterChain连起来，在http请求时
进行检查。

---
HttpSecurity是在使用SpringSecurity中可能会用到的配置。

# `HttpSecurity`
有这4个fields:

{% highlight java %}
private final RequestMatcherConfigurer requestMatcherConfigurer;
private List<Filter> filters = new ArrayList<Filter>();
private RequestMatcher requestMatcher = AnyRequestMatcher.INSTANCE;
private FilterComparator comparator = new FilterComparator();
{% endhighlight %}

1. RequestMatcherConfigurer 一个RequestMatcher的chain，类中有一个List<RequestMatcher>
2. Filters  一系列的过滤器
3. RequestMatcher Url的匹配器
4. FilterComparator 一系列的filter以及对应的顺序，排序用的，在performBuild方法中

## `RequestMatcher`
{% highlight java %}
public interface RequestMatcher {
	boolean matches(HttpServletRequest var1);
}
{% endhighlight %}
用来匹配HttpServletRequest。实现有很多:
1. AndPathRequestMatcher 对一个RequestMatcher的list进行判断是否全部都match
2. AntPathRequestMatcher Ant-Style的path匹配
3. MvcRequestMatcher 比较HttpMethod，ServletPath，AntPath
4. AnyRequestMatcher matches方法一直返回true
还有其它的实现，在用到时直接看源码。


httpSecurity相关的配置:
1. OpenIDLoginConfigurer
2. HeadersConfigurer
3. CorsConfigurer
4. SessionManagementConfigurer
5. PortMapperConfigurer
6. JeeConfigurer
7. X509Configurer
8. RememberMeConfigurer
9. ExpressionUrlAuthorizationConfigurer
10. RequestCacheConfigurer
11. ExceptionHandlingConfigurer
12. SecurityContextConfigurer
13. ServletApiConfigurer
14. CsrfConfigurer
15. LogoutConfigurer
16. AnonymousConfigurer
17. FormLoginConfigurer 登录配置
18. ChannelSecurityConfigurer
19. HttpBasicConfigurer
20. RequestMatcherConfigurer

还有一些是HttpSecurity自已用到的方法
1. authenticationProvider
2. userDetailsService
3. addFilterAfter
4. addFilter
5. addFilterAt
6. requestMatcher
7. antMatcher
8. mvcMatcher
9. regexMatcher

---

# spring-scurity的login认证配置，FormLoginConfigurer

> 整体思路:在HttpSecurity中添加FormLoginConfigurer，他默认有UsernamePasswordAuthenticationFilter，在访问网站时，这个过滤器会拦截你的请求，跳转到你设定的url上，输入用户名和密码之后，会通过AuthenticationManager中的AuthenticationProvider进行验证，通过之后，就会根据设定的跳转策略去跳转。

{% highlight java %}
public class SecurityConfig extends WebSecurityConfigurerAdapter {
	@Override
	protected void configure(HttpSecurity http) throws Exception {
		http
			.formLogin();
	}
}
{% endhighlight %}

看一下FormLoginConfigurer的实现uml:

<img src="{{site.baseurl}}/assets/images/spring-security/spring-security-form-login-configurer.png"/>

配置默认登录表单
相关的配置在FormLoginConfigurer中(类似的功能还有OpenIDLoginConfigurer):

1. loginPage 登录的的页面
2. usernameParameter 获取username的key
3. passwordParameter 获取password的key
4. failureForwardUrl 失败跳转的Url
5. successForwardUrl 成功跳转的Url

FormLoginConfigurer继承了AbstractAuthenticationFilterConfigurer中的一些功能:

1. defaultSuccessUrl(proccessUrl, alwaysUseDefautUrl) 设置认证成功后的url，和successForwardUrl、failureForwardUrl相同
2. loginProcessingUrl 处理登录事件的Url
3. authenticationDetailsSource
4. successHandler
5. failureUrl
6. failureHandler

---

## `AbstractAuthenticationFilterConfigurer`
主要设置了login的Url，Handler，添加了filter，以及login的入口。
参考registerDefaultAuthenticationEntryPoint方法。 

---

### `UernamePasswordAuthenticationFilter`
设置的requiresAuthenticationRequestMatcher为"/login" POST方法，表示这个就是默认入口。
他继承了AbstractAuthenticationProcessingFilter，这个filter会调用attemptAuthentication来获取Authentication。
在UsernamePasswordAuthenticationFilter中，通过实现了ProviderManager接口方法authenticate的AuthenticationManager来验证。
得到Authentication之后会触发SuccessHandler，调用onAuthenticationSuccess，默认实现是转发到对应的SuccessUrl。

用UsernamePasswordAuthenticationToken来构建用户的凭证，通过AuthenticationManager(ProviderManager来验证。
AuthenticationManager中用每一个provider(AbstractUserDetailsAuthenticationProvider)来验证，也就是验证UsernamePasswordAuthenticationToken。
provider可自定义。

AbstractUserDetailsAuthenticationProvider的认证方法:
1. 根据用户名和token，获取User通过retrieveUser方法
2. preCheck(User)
3. additionCheck(User)
4. 把User放入userCache中
5. 返回正确的Authentication，然后广播认证结果

---

## `SimpleUrlAuthenticationSuccessHandler`

他实现了AbstractAuthenticationTargetUrlRequestHandler和AuthenticationSuccessHandler。
SimpleUrlAuthenticationSuccessHandler做了两件事:
1. 设置了defaultTargetUrl
2. 用clearAuthenticationAttributes方法清空了session中SPRING_SECURITY_LAST_EXCEPTION对应的信息

---

## `AuthenticationSuccessHandler`

{% highlight java %}
public interface AuthenticationSuccessHandler {
	void onAuthenticationSuccess(HttpServletRequest request,
			HttpServletResponse response, Authentication authentication)
			throws IOException, ServletException;)	
}
{% endhighlight %}

是用来处理认证成功后的操作。

---

## `AbstractAuthenticationTargetUrlRequestHandler`

{% highlight java %}
protected void handle(HttpServletRequest request, HttpServletResponse response,
	Authentication authentication) throws IOException, ServletException {
	String targetUrl = determineTargetUrl(request, response);
	if (response.isCommitted()) {
		logger.debug("Response has already been committed. Unable to redirect to "
				+ targetUrl);
		return;
	}
						
	redirectStrategy.sendRedirect(request, response, targetUrl);
}
{% endhighlight %}

获取targetUrl之后，再***重定向***，如果获取不到，否则返回。

获取targetUrl的过程:
1. 通过alwaysUseDefaultTargetUrl来判断是否使用默认的targetUrl(为'/')
2. 从request的parameter中获取对应targetUrlParameter的值
3. 通过userReferer来判断是否使用Referer作为targetUrl
4. 如果以上条件都没找到targetUrl，则使用默认的targetUrl

得到targetUrl之后，看response是否被committed，如果没有，则***重定向***到targetUrl。

--- 
和SimpleUrlAuthenticationSuccessHandler类似的还有SimpleUrlLogoutSuccessHandler, SavedRequestAwareAuthenticationSuccessHandler。

