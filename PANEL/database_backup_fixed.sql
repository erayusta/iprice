-- Data for table: users
INSERT INTO users (id, name, email, email_verified_at, password, remember_token, created_at, updated_at, iprice_token) VALUES (2, 'SERKAN ODACI', 'serkan.odaci@emind.com.tr', NULL, '$2y$12$Kbmrsa70V/vYzPyQZqMCBub1vWuQz3utl19yw4pFRzssy336Qz5SK', NULL, '2025-10-08 18:18:25', '2025-10-08 18:18:49', NULL);

-- Data for table: attributes
INSERT INTO attributes (id, name, type, description, attributes, created_at, updated_at) VALUES (1, 'price', 'text', NULL, NULL, '2025-10-08 18:07:12', '2025-10-08 18:07:12');
INSERT INTO attributes (id, name, type, description, attributes, created_at, updated_at) VALUES (2, 'sale_price', 'text', NULL, NULL, '2025-10-08 18:07:12', '2025-10-08 18:07:12');
INSERT INTO attributes (id, name, type, description, attributes, created_at, updated_at) VALUES (3, 'shipment_duration', 'text', NULL, NULL, '2025-10-08 18:07:12', '2025-10-08 18:07:12');
INSERT INTO attributes (id, name, type, description, attributes, created_at, updated_at) VALUES (4, 'is_resale', 'boolean', NULL, NULL, '2025-10-08 18:07:12', '2025-10-08 18:07:12');
INSERT INTO attributes (id, name, type, description, attributes, created_at, updated_at) VALUES (5, 'is_outlet', 'boolean', NULL, NULL, '2025-10-08 18:07:13', '2025-10-08 18:07:13');
INSERT INTO attributes (id, name, type, description, attributes, created_at, updated_at) VALUES (6, 'is_stock', 'boolean', NULL, NULL, '2025-10-08 18:07:13', '2025-10-08 18:07:13');
INSERT INTO attributes (id, name, type, description, attributes, created_at, updated_at) VALUES (7, 'is_redirect', 'boolean', NULL, NULL, '2025-10-08 18:07:13', '2025-10-08 18:07:13');
INSERT INTO attributes (id, name, type, description, attributes, created_at, updated_at) VALUES (8, 'multi_price', 'text', NULL, NULL, '2025-10-08 18:07:13', '2025-10-08 18:07:13');
INSERT INTO attributes (id, name, type, description, attributes, created_at, updated_at) VALUES (9, 'seller', 'text', NULL, NULL, '2025-10-08 18:07:13', '2025-10-08 18:07:13');
INSERT INTO attributes (id, name, type, description, attributes, created_at, updated_at) VALUES (10, 'sub_price', 'text', NULL, NULL, '2025-10-08 18:07:14', '2025-10-08 18:07:14');
INSERT INTO attributes (id, name, type, description, attributes, created_at, updated_at) VALUES (11, 'last_30_day_price', 'text', NULL, NULL, '2025-10-08 18:07:14', '2025-10-08 18:07:14');
INSERT INTO attributes (id, name, type, description, attributes, created_at, updated_at) VALUES (12, 'premium_price', 'text', NULL, NULL, '2025-10-08 18:07:14', '2025-10-08 18:07:14');
INSERT INTO attributes (id, name, type, description, attributes, created_at, updated_at) VALUES (13, 'other_seller_button', 'text', NULL, NULL, '2025-10-08 18:07:14', '2025-10-08 18:07:14');
INSERT INTO attributes (id, name, type, description, attributes, created_at, updated_at) VALUES (14, 'seller_name_in_modal', 'text', NULL, NULL, '2025-10-08 18:07:14', '2025-10-08 18:07:14');
INSERT INTO attributes (id, name, type, description, attributes, created_at, updated_at) VALUES (15, 'seller_price_in_modal', 'text', NULL, NULL, '2025-10-08 18:07:15', '2025-10-08 18:07:15');
INSERT INTO attributes (id, name, type, description, attributes, created_at, updated_at) VALUES (16, 'seller_container_xpath', 'text', NULL, NULL, '2025-10-08 18:07:15', '2025-10-08 18:07:15');
INSERT INTO attributes (id, name, type, description, attributes, created_at, updated_at) VALUES (17, 'shipping_element', 'text', NULL, NULL, '2025-10-08 18:07:15', '2025-10-08 18:07:15');
INSERT INTO attributes (id, name, type, description, attributes, created_at, updated_at) VALUES (18, 'on_page_seller_name', 'text', NULL, NULL, '2025-10-08 18:07:15', '2025-10-08 18:07:15');
INSERT INTO attributes (id, name, type, description, attributes, created_at, updated_at) VALUES (19, 'on_page_seller_price', 'text', NULL, NULL, '2025-10-08 18:07:16', '2025-10-08 18:07:16');
INSERT INTO attributes (id, name, type, description, attributes, created_at, updated_at) VALUES (20, 'on_page_seller_shipping', 'text', NULL, NULL, '2025-10-08 18:07:16', '2025-10-08 18:07:16');
INSERT INTO attributes (id, name, type, description, attributes, created_at, updated_at) VALUES (21, 'other_seller_url', 'text', NULL, NULL, '2025-10-08 18:07:16', '2025-10-08 18:07:16');

-- Data for table: roles
INSERT INTO roles (id, name, guard_name, created_at, updated_at) VALUES (1, 'Admin', 'web', '2025-10-08 18:13:58', '2025-10-08 18:13:58');
INSERT INTO roles (id, name, guard_name, created_at, updated_at) VALUES (2, 'Kullanıcı', 'web', '2025-10-08 18:14:05', '2025-10-08 18:14:05');

-- Data for table: permissions
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (1, 'companies.view', 'web', '2025-10-08 18:11:07', '2025-10-08 18:11:07');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (2, 'companies.create', 'web', '2025-10-08 18:11:07', '2025-10-08 18:11:07');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (3, 'companies.edit', 'web', '2025-10-08 18:11:08', '2025-10-08 18:11:08');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (4, 'companies.delete', 'web', '2025-10-08 18:11:08', '2025-10-08 18:11:08');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (5, 'products.view', 'web', '2025-10-08 18:11:09', '2025-10-08 18:11:09');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (6, 'products.create', 'web', '2025-10-08 18:11:09', '2025-10-08 18:11:09');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (7, 'products.edit', 'web', '2025-10-08 18:11:09', '2025-10-08 18:11:09');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (8, 'products.delete', 'web', '2025-10-08 18:11:10', '2025-10-08 18:11:10');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (9, 'products.show', 'web', '2025-10-08 18:11:10', '2025-10-08 18:11:10');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (10, 'products_url.show', 'web', '2025-10-08 18:11:11', '2025-10-08 18:11:11');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (11, 'products_url.edit', 'web', '2025-10-08 18:11:11', '2025-10-08 18:11:11');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (12, 'product_list.show', 'web', '2025-10-08 18:11:11', '2025-10-08 18:11:11');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (13, 'product_list.xmlimport', 'web', '2025-10-08 18:11:12', '2025-10-08 18:11:12');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (14, 'product_list.add', 'web', '2025-10-08 18:11:12', '2025-10-08 18:11:12');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (15, 'product_list.edit', 'web', '2025-10-08 18:11:13', '2025-10-08 18:11:13');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (16, 'product_list.delete', 'web', '2025-10-08 18:11:13', '2025-10-08 18:11:13');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (17, 'brands.show', 'web', '2025-10-08 18:11:13', '2025-10-08 18:11:13');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (18, 'brands.add', 'web', '2025-10-08 18:11:14', '2025-10-08 18:11:14');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (19, 'brands.edit', 'web', '2025-10-08 18:11:14', '2025-10-08 18:11:14');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (20, 'brands.delete', 'web', '2025-10-08 18:11:14', '2025-10-08 18:11:14');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (21, 'operations.show', 'web', '2025-10-08 18:11:15', '2025-10-08 18:11:15');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (22, 'scan.show', 'web', '2025-10-08 18:11:15', '2025-10-08 18:11:15');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (23, 'scan.fast', 'web', '2025-10-08 18:11:16', '2025-10-08 18:11:16');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (24, 'scan.plan', 'web', '2025-10-08 18:11:16', '2025-10-08 18:11:16');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (25, 'privateanalysis.show', 'web', '2025-10-08 18:11:16', '2025-10-08 18:11:16');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (26, 'privateanalysis.add', 'web', '2025-10-08 18:11:17', '2025-10-08 18:11:17');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (27, 'privateanalysis.edit', 'web', '2025-10-08 18:11:17', '2025-10-08 18:11:17');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (28, 'privateanalysis.delete', 'web', '2025-10-08 18:11:18', '2025-10-08 18:11:18');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (29, 'privateanalysis.view', 'web', '2025-10-08 18:11:18', '2025-10-08 18:11:18');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (30, 'companies.add', 'web', '2025-10-08 18:20:22', '2025-10-08 18:20:22');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (31, 'companies.attribute', 'web', '2025-10-08 18:20:23', '2025-10-08 18:20:23');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (32, 'companies.show', 'web', '2025-10-08 18:21:23', '2025-10-08 18:21:23');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (33, 'members.show', 'web', '2025-10-08 18:23:22', '2025-10-08 18:23:22');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (34, 'roles.show', 'web', '2025-10-08 18:23:23', '2025-10-08 18:23:23');
INSERT INTO permissions (id, name, guard_name, created_at, updated_at) VALUES (35, 'attributes.show', 'web', '2025-10-08 18:23:24', '2025-10-08 18:23:24');

-- Data for table: role_permissions
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (1, 1, 1, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (2, 1, 2, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (3, 1, 3, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (4, 1, 4, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (5, 1, 5, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (6, 1, 6, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (7, 1, 7, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (8, 1, 8, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (9, 1, 9, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (10, 1, 10, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (11, 1, 11, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (12, 1, 12, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (13, 1, 13, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (14, 1, 14, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (15, 1, 15, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (16, 1, 16, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (17, 1, 17, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (18, 1, 18, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (19, 1, 19, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (20, 1, 20, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (21, 1, 21, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (22, 1, 22, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (23, 1, 23, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (24, 1, 24, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (25, 1, 25, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (26, 1, 26, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (27, 1, 27, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (28, 1, 28, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (29, 1, 29, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (30, 1, 30, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (31, 1, 31, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (32, 1, 32, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (33, 1, 33, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (34, 1, 34, NULL, NULL);
INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at) VALUES (35, 1, 35, NULL, NULL);

-- Data for table: user_roles
INSERT INTO user_roles (id, user_id, role_id, created_at, updated_at) VALUES (1, 2, 1, NULL, NULL);
