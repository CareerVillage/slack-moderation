require 'spec_helper'

describe 'locales::params', :type => :class do
  context "On a Debian OS" do
    let :facts do
      {
        :osfamily               => 'Debian',
        :operatingsystemrelease => '6',
        :lsbdistcodename        => 'squeeze',
        :operatingsystem        => 'Debian',
        :kernel                 => 'Linux',
      }
    end

    it { is_expected.to compile.with_all_deps }
    it { is_expected.to have_resource_count(0) }
  end
end