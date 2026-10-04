create table if not exists users (
  id varchar(32) primary key,
  email varchar(200) not null unique,
  name varchar(200) not null,
  pw_hash varchar(100) not null,
  created_at bigint not null
);
create table if not exists sessions (
  token varchar(64) primary key,
  user_id varchar(32) not null,
  created_at bigint not null
);
create table if not exists subscriptions (
  user_id varchar(32) primary key,
  plan varchar(20) not null,
  period varchar(10) not null,
  status varchar(20) not null,
  channel varchar(20) not null,
  trial_ends_at bigint not null,
  renews_at bigint not null,
  created_at bigint not null
);
create table if not exists shops (
  id varchar(32) primary key,
  owner_id varchar(32) not null,
  name varchar(200) not null,
  type varchar(30) not null,
  country varchar(2) not null,
  currency varchar(3) not null,
  locale varchar(10) not null,
  till varchar(40),
  created_at bigint not null
);
create table if not exists members (
  shop_id varchar(32) not null,
  user_id varchar(32) not null,
  role varchar(20) not null,
  primary key (shop_id, user_id)
);
create table if not exists products (
  id varchar(32) primary key,
  shop_id varchar(32) not null,
  name varchar(200) not null,
  category varchar(60) not null,
  price bigint not null,
  stock int not null,
  barcode varchar(60),
  low_at int not null default 10,
  active boolean not null default true,
  updated_at bigint not null
);
create index if not exists idx_products_shop on products(shop_id);
create table if not exists sales (
  id varchar(32) primary key,
  shop_id varchar(32) not null,
  number int not null,
  user_id varchar(32) not null,
  tender varchar(20) not null,
  tender_ref varchar(40),
  total bigint not null,
  vat bigint not null,
  currency varchar(3) not null,
  status varchar(12) not null,
  idem_key varchar(80) not null,
  created_at bigint not null,
  unique (shop_id, idem_key)
);
create index if not exists idx_sales_shop_time on sales(shop_id, created_at);
create table if not exists sale_lines (
  id varchar(32) primary key,
  sale_id varchar(32) not null,
  product_id varchar(32) not null,
  name varchar(200) not null,
  qty int not null,
  unit_price bigint not null,
  serial varchar(80)
);
create index if not exists idx_lines_sale on sale_lines(sale_id);
create table if not exists activity (
  id varchar(32) primary key,
  shop_id varchar(32) not null,
  user_id varchar(32),
  user_name varchar(200) not null,
  kind varchar(30) not null,
  data varchar(2000) not null,
  device varchar(60) not null,
  created_at bigint not null
);
create index if not exists idx_activity_shop on activity(shop_id, created_at);
create table if not exists float_accounts (
  shop_id varchar(32) not null,
  network varchar(20) not null,
  balance bigint not null,
  low_at bigint not null,
  primary key (shop_id, network)
);
create table if not exists float_tx (
  id varchar(32) primary key,
  shop_id varchar(32) not null,
  user_id varchar(32) not null,
  user_name varchar(200) not null,
  network varchar(20) not null,
  kind varchar(20) not null,
  amount bigint not null,
  commission bigint not null,
  created_at bigint not null
);
create index if not exists idx_float_tx_shop on float_tx(shop_id, created_at);
