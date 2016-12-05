Puppet::Parser::Functions.newfunction(:get_py_value) do |arg|
    value = lookupvar(arg)
    if value == '__NONE__'
        return 'None'
    elsif value == '__EMPTY__'
        return "''"
    else
        return "'#{value}'"
    end
end