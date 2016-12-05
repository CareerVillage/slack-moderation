describe package('locales') do
  it { should be_installed }
end

describe command('echo $LANG') do
  its('stdout') { should eq "zh_CN.UTF-8\n" }
end
