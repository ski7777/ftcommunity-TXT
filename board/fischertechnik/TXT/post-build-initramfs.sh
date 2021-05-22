#!/bin/bash
TARGET=$1
mv $TARGET/lib/modules/* ../build/modules || true
