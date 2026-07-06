"""
Spring Boot 代码生成工具
提供根据参数表元数据生成完整Spring Boot项目代码的功能
"""


class SpringBootCodeGenerator:
    """
    Spring Boot代码生成器
    根据参数表元数据生成完整的Spring Boot项目代码，包括：
    Entity、DTO、Mapper、Service、ServiceImpl、Controller、Mapper XML等
    """

    def __init__(self, table, fields, package_name='com.example', module_name='demo'):
        """
        初始化代码生成器
        
        Args:
            table: 参数表对象
            fields: 字段定义列表
            package_name: Java包名
            module_name: 模块名
        """
        self.table = table
        self.fields = fields
        self.package_name = package_name
        self.module_name = module_name
        self.entity_name = table.name.replace('代码表', '')
        self.table_name = table.name.replace('代码表', '').lower()
        self.package_path = package_name.replace('.', '/')

    def generate_all(self):
        """
        生成所有代码文件
        
        Returns:
            dict: 包含所有代码文件内容的字典
        """
        return {
            'entity': self.generate_entity(),
            'dto': self.generate_dto(),
            'mapper': self.generate_mapper(),
            'service': self.generate_service(),
            'service_impl': self.generate_service_impl(),
            'controller': self.generate_controller(),
            'mapper_xml': self.generate_mapper_xml(),
            'pom': self.generate_pom(),
            'application': self.generate_application(),
            'application_yaml': self.generate_application_yaml(),
        }

    def generate_entity(self):
        """生成Entity实体类"""
        field_code = ''
        for field in self.fields:
            java_type = self._get_java_type(field.field_type, field.length)
            field_name = field.field_name
            display_name = field.display_name
            is_required = '@NotBlank' if field.is_required else ''
            field_code += f"""
    /**
     * {display_name}
     */
    {is_required}
    private {java_type} {field_name};
"""
        return f"""package {self.package_name}.{self.module_name}.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import java.io.Serializable;
import java.math.BigDecimal;
import java.util.Date;

/**
 * {self.table.name}实体类
 * {self.table.business_description}
 */
@Entity
@Table(name = "{self.table_name}")
public class {self.entity_name} implements Serializable {{

    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

{field_code}
    // Getters and Setters
    public Long getId() {{ return id; }}
    public void setId(Long id) {{ this.id = id; }}
{self._generate_getters_setters()}
}}
"""

    def generate_dto(self):
        """生成DTO数据传输对象"""
        field_code = ''
        for field in self.fields:
            java_type = self._get_java_type(field.field_type, field.length)
            field_name = field.field_name
            display_name = field.display_name
            is_required = '@NotBlank' if field.is_required else ''
            field_code += f"""
    /**
     * {display_name}
     */
    {is_required}
    private {java_type} {field_name};
"""
        return f"""package {self.package_name}.{self.module_name}.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/**
 * {self.table.name}数据传输对象
 */
@Data
public class {self.entity_name}DTO {{

{field_code}
}}
"""

    def generate_mapper(self):
        """生成Mapper接口"""
        return f"""package {self.package_name}.{self.module_name}.mapper;

import {self.package_name}.{self.module_name}.entity.{self.entity_name};
import org.apache.ibatis.annotations.Mapper;
import java.util.List;

/**
 * {self.table.name}Mapper接口
 */
@Mapper
public interface {self.entity_name}Mapper {{

    /**
     * 根据ID查询
     */
    {self.entity_name} selectById(Long id);

    /**
     * 查询所有
     */
    List<{self.entity_name}> selectAll();

    /**
     * 根据条件查询
     */
    List<{self.entity_name}> selectByCondition({self.entity_name} entity);

    /**
     * 新增
     */
    int insert({self.entity_name} entity);

    /**
     * 更新
     */
    int updateById({self.entity_name} entity);

    /**
     * 删除
     */
    int deleteById(Long id);
}}
"""

    def generate_service(self):
        """生成Service接口"""
        return f"""package {self.package_name}.{self.module_name}.service;

import {self.package_name}.{self.module_name}.dto.{self.entity_name}DTO;
import {self.package_name}.{self.module_name}.entity.{self.entity_name};
import java.util.List;

/**
 * {self.table.name}Service接口
 */
public interface {self.entity_name}Service {{

    /**
     * 根据ID查询
     */
    {self.entity_name} findById(Long id);

    /**
     * 查询所有
     */
    List<{self.entity_name}> findAll();

    /**
     * 根据条件查询
     */
    List<{self.entity_name}> findByCondition({self.entity_name}DTO dto);

    /**
     * 新增
     */
    {self.entity_name} create({self.entity_name}DTO dto);

    /**
     * 更新
     */
    {self.entity_name} update(Long id, {self.entity_name}DTO dto);

    /**
     * 删除
     */
    void delete(Long id);
}}
"""

    def generate_service_impl(self):
        """生成ServiceImpl实现类"""
        entity_var = self.entity_name[0].lower() + self.entity_name[1:]
        return f"""package {self.package_name}.{self.module_name}.service.impl;

import {self.package_name}.{self.module_name}.dto.{self.entity_name}DTO;
import {self.package_name}.{self.module_name}.entity.{self.entity_name};
import {self.package_name}.{self.module_name}.mapper.{self.entity_name}Mapper;
import {self.package_name}.{self.module_name}.service.{self.entity_name}Service;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

/**
 * {self.table.name}ServiceImpl实现类
 */
@Service
@Transactional
public class {self.entity_name}ServiceImpl implements {self.entity_name}Service {{

    private final {self.entity_name}Mapper {entity_var}Mapper;

    public {self.entity_name}ServiceImpl({self.entity_name}Mapper {entity_var}Mapper) {{
        this.{entity_var}Mapper = {entity_var}Mapper;
    }}

    @Override
    @Transactional(readOnly = true)
    public {self.entity_name} findById(Long id) {{
        return {entity_var}Mapper.selectById(id);
    }}

    @Override
    @Transactional(readOnly = true)
    public List<{self.entity_name}> findAll() {{
        return {entity_var}Mapper.selectAll();
    }}

    @Override
    @Transactional(readOnly = true)
    public List<{self.entity_name}> findByCondition({self.entity_name}DTO dto) {{
        {self.entity_name} entity = new {self.entity_name}();
        BeanUtils.copyProperties(dto, entity);
        return {entity_var}Mapper.selectByCondition(entity);
    }}

    @Override
    public {self.entity_name} create({self.entity_name}DTO dto) {{
        {self.entity_name} entity = new {self.entity_name}();
        BeanUtils.copyProperties(dto, entity);
        {entity_var}Mapper.insert(entity);
        return entity;
    }}

    @Override
    public {self.entity_name} update(Long id, {self.entity_name}DTO dto) {{
        {self.entity_name} entity = {entity_var}Mapper.selectById(id);
        if (entity == null) {{
            throw new RuntimeException("{self.entity_name}不存在");
        }}
        BeanUtils.copyProperties(dto, entity);
        entity.setId(id);
        {entity_var}Mapper.updateById(entity);
        return entity;
    }}

    @Override
    public void delete(Long id) {{
        {self.entity_name} entity = {entity_var}Mapper.selectById(id);
        if (entity == null) {{
            throw new RuntimeException("{self.entity_name}不存在");
        }}
        {entity_var}Mapper.deleteById(id);
    }}
}}
"""

    def generate_controller(self):
        """生成Controller控制器"""
        entity_var = self.entity_name[0].lower() + self.entity_name[1:]
        api_name = self.entity_name.lower()
        return f"""package {self.package_name}.{self.module_name}.controller;

import {self.package_name}.{self.module_name}.dto.{self.entity_name}DTO;
import {self.package_name}.{self.module_name}.entity.{self.entity_name};
import {self.package_name}.{self.module_name}.service.{self.entity_name}Service;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;
import java.util.List;

/**
 * {self.table.name}Controller控制器
 */
@RestController
@RequestMapping("/api/{api_name}")
public class {self.entity_name}Controller {{

    private final {self.entity_name}Service {entity_var}Service;

    public {self.entity_name}Controller({self.entity_name}Service {entity_var}Service) {{
        this.{entity_var}Service = {entity_var}Service;
    }}

    /**
     * 根据ID查询
     */
    @GetMapping("/{{id}}")
    public ResponseEntity<{self.entity_name}> getById(@PathVariable Long id) {{
        {self.entity_name} entity = {entity_var}Service.findById(id);
        return ResponseEntity.ok(entity);
    }}

    /**
     * 查询所有
     */
    @GetMapping
    public ResponseEntity<List<{self.entity_name}>> getAll() {{
        List<{self.entity_name}> list = {entity_var}Service.findAll();
        return ResponseEntity.ok(list);
    }}

    /**
     * 根据条件查询
     */
    @PostMapping("/search")
    public ResponseEntity<List<{self.entity_name}>> search(@RequestBody {self.entity_name}DTO dto) {{
        List<{self.entity_name}> list = {entity_var}Service.findByCondition(dto);
        return ResponseEntity.ok(list);
    }}

    /**
     * 新增
     */
    @PostMapping
    public ResponseEntity<{self.entity_name}> create(@Validated @RequestBody {self.entity_name}DTO dto) {{
        {self.entity_name} entity = {entity_var}Service.create(dto);
        return ResponseEntity.ok(entity);
    }}

    /**
     * 更新
     */
    @PutMapping("/{{id}}")
    public ResponseEntity<{self.entity_name}> update(@PathVariable Long id, @Validated @RequestBody {self.entity_name}DTO dto) {{
        {self.entity_name} entity = {entity_var}Service.update(id, dto);
        return ResponseEntity.ok(entity);
    }}

    /**
     * 删除
     */
    @DeleteMapping("/{{id}}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {{
        {entity_var}Service.delete(id);
        return ResponseEntity.ok().build();
    }}
}}
"""

    def generate_mapper_xml(self):
        """生成Mapper XML文件"""
        base_columns = ','.join([f.field_name for f in self.fields])
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="{self.package_name}.{self.module_name}.mapper.{self.entity_name}Mapper">

    <resultMap id="BaseResultMap" type="{self.entity_name}">
        <id column="id" property="id"/>
{self._generate_result_map()}
    </resultMap>

    <sql id="Base_Column_List">
        id, {base_columns}
    </sql>

    <select id="selectById" resultMap="BaseResultMap">
        SELECT <include refid="Base_Column_List"/>
        FROM {self.table_name}
        WHERE id = #{{id}}
    </select>

    <select id="selectAll" resultMap="BaseResultMap">
        SELECT <include refid="Base_Column_List"/>
        FROM {self.table_name}
        ORDER BY id DESC
    </select>

    <select id="selectByCondition" resultMap="BaseResultMap" parameterType="{self.entity_name}">
        SELECT <include refid="Base_Column_List"/>
        FROM {self.table_name}
        <where>
{self._generate_where_conditions()}
        </where>
        ORDER BY id DESC
    </select>

    <insert id="insert" parameterType="{self.entity_name}" useGeneratedKeys="true" keyProperty="id">
        INSERT INTO {self.table_name} ({base_columns})
        VALUES ({','.join([f'#{{{f.field_name}}}' for f in self.fields])})
    </insert>

    <update id="updateById" parameterType="{self.entity_name}">
        UPDATE {self.table_name}
        <set>
{self._generate_set_clause()}
        </set>
        WHERE id = #{{id}}
    </update>

    <delete id="deleteById">
        DELETE FROM {self.table_name} WHERE id = #{{id}}
    </delete>

</mapper>
"""

    def generate_pom(self):
        """生成pom.xml"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>{self.package_name}</groupId>
    <artifactId>{self.module_name}</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <packaging>jar</packaging>

    <name>{self.module_name}</name>
    <description>{self.module_name} Spring Boot Application</description>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
        <relativePath/>
    </parent>

    <properties>
        <java.version>21</java.version>
        <mybatis-spring-boot-starter.version>3.0.2</mybatis-spring-boot-starter.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>

        <dependency>
            <groupId>org.mybatis.spring.boot</groupId>
            <artifactId>mybatis-spring-boot-starter</artifactId>
            <version>${{mybatis-spring-boot-starter.version}}</version>
        </dependency>

        <dependency>
            <groupId>com.mysql</groupId>
            <artifactId>mysql-connector-j</artifactId>
            <scope>runtime</scope>
        </dependency>

        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>

</project>
"""

    def generate_application(self):
        """生成Application启动类"""
        return f"""package {self.package_name}.{self.module_name};

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.mybatis.spring.annotation.MapperScan;

/**
 * {self.module_name} Spring Boot 启动类
 */
@SpringBootApplication
@MapperScan("{self.package_name}.{self.module_name}.mapper")
public class {self.module_name.capitalize()}Application {{

    public static void main(String[] args) {{
        SpringApplication.run({self.module_name.capitalize()}Application.class, args);
    }}
}}
"""

    def generate_application_yaml(self):
        """生成application.yml配置文件"""
        return f"""server:
  port: 8080

spring:
  application:
    name: {self.module_name}
  
  datasource:
    url: jdbc:mysql://localhost:3306/{self.module_name}_db?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai
    username: root
    password: root
    driver-class-name: com.mysql.cj.jdbc.Driver

mybatis:
  mapper-locations: classpath:mapper/*.xml
  type-aliases-package: {self.package_name}.{self.module_name}.entity

logging:
  level:
    {self.package_name}.{self.module_name}.mapper: DEBUG
"""

    def _get_java_type(self, field_type, length):
        """字段类型到Java类型的映射"""
        type_mapping = {
            'string': 'String',
            'integer': 'Integer',
            'decimal': 'BigDecimal',
            'date': 'Date',
            'datetime': 'Date',
            'boolean': 'Boolean',
            'text': 'String',
        }
        return type_mapping.get(field_type, 'String')

    def _generate_getters_setters(self):
        """生成getter和setter方法"""
        code = ''
        for field in self.fields:
            java_type = self._get_java_type(field.field_type, field.length)
            field_name = field.field_name
            capitalized = field_name[0].upper() + field_name[1:]
            code += f"""
    public {java_type} get{capitalized}() {{ return {field_name}; }}
    public void set{capitalized}({java_type} {field_name}) {{ this.{field_name} = {field_name}; }}"""
        return code

    def _generate_result_map(self):
        """生成MyBatis ResultMap字段映射"""
        code = ''
        for field in self.fields:
            code += f"""        <result column="{field.field_name}" property="{field.field_name}"/>\n"""
        return code

    def _generate_where_conditions(self):
        """生成MyBatis动态查询条件"""
        code = ''
        for field in self.fields:
            code += f"""            <if test="{field.field_name} != null">AND {field.field_name} = #{{{field.field_name}}}</if>\n"""
        return code

    def _generate_set_clause(self):
        """生成MyBatis动态更新SET子句"""
        code = ''
        for field in self.fields:
            code += f"""            <if test="{field.field_name} != null">{field.field_name} = #{{{field.field_name}}},</if>\n"""
        return code
