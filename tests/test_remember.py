from shorthand import generate as gen

def test_remember():
    correct_shorthand = "r" + gen.SH_DELIM + "mmb" + gen.SH_DELIM + "r"
    generated_shorthand = gen.get_gen_algo_fn()('remember')['remember']['shorthand']
    assert correct_shorthand == generated_shorthand