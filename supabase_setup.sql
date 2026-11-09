-- Run this once in Supabase: SQL Editor -> New query -> paste -> Run
create table if not exists tx (
  id bigint generated always as identity primary key,
  date date not null,
  description text not null,
  amount numeric not null,
  unique (date, description, amount)
);
-- Demo only: lets the app read and write with the anon key
alter table tx disable row level security;